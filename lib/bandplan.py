# ***********************************************************************************
# Module that generates svg bandplan
# ***********************************************************************************
__author__ = "IU1BOW - Corrado"
from datetime import date
from svgwrite import Drawing
import base64
import logging

class BandPlan:

    def __init__(self, logger, bands, modes, icon_logo):
        """
        Initializes the BandPlan generator.

        Args:
            logger: Logger instance for logging messages.
            bands (dict): Dictionary containing band information ('bands' key).
            modes (dict): Dictionary containing mode information ('modes' key).
            icon_logo (str): Path to the logo image file.
        """
        self.logger = logger
        self.logger.info("Class: %s init start", self.__class__.__name__)
        self.bands = bands['bands']
        self.modes = modes

        # Fixed variables
        self.margin_left = 140
        self.margin_right = 20
        self.margin_top = 50
        self.margin_bottom = 50
        self.chart_width = 1600
        self.legend_margin = 5
        self.footer_height = 30  # Adjusted footer height
        self.legend_height = self.mode_height = 10
        self.text_height = 12
        self.size_ft_square = self.mode_height / 2
        self.band_spacing = 2
        self.mode_spacing = 2

        self.font_family = 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif'
        self.font_size = self.text_height

        # Define mode colors
        self.mode_colors = {
            'cw': '#FFA500',
            'digi': '#4169E1',
            'digi-ft4': '#00CED1',
            'digi-ft8': '#800080',
            'phone': '#228B22'
        }
        self.legend_offset_x = 100
        self.logo_path = icon_logo
        self.github_link = "https://github.com/coulisse/spiderweb/"
        self.title = 'Amateur radio band plan'

    def __scale_f(self, freq, band_min, band_max, width):
        return ((freq - band_min) / (band_max - band_min)) * width

    def __convert_frequency(self, value, umis=None):
        if value < 1000000:
            formatted = f"{value / 1000:.3f}".rstrip('0').rstrip('.')
            return f"{formatted} MHz" if umis else formatted
        else:
            formatted = f"{value / 1000000:.3f}".rstrip('0').rstrip('.')
            return f"{formatted} GHz" if umis else formatted

    def __draw_legend(self, font_group, dwg, y):
        # Add legend
        legend_x = self.chart_width - self.margin_right - 200
        legend_y = y

        # Define legend rectangle in defs
        dwg.defs.add(dwg.rect(id="legend_rect", size=(self.legend_height, self.legend_height)))

        # Add legend squares without drawing a rectangle in the top left corner
        for count, (mode, color) in enumerate(self.mode_colors.items()):
            font_group.add(dwg.use('#legend_rect', insert=(legend_x, legend_y), fill=color))
            font_group.add(dwg.text(mode, insert=(legend_x + self.legend_height + self.legend_margin, legend_y + self.legend_height / 2), fill='black', font_size='12px', text_anchor='start'))

            if count % 2 == 0:
                legend_x += self.legend_offset_x
            else:
                legend_x = self.chart_width - self.margin_right - 200
                legend_y += self.legend_height + self.legend_margin

        # Add space after the last legend item
        y = legend_y + self.legend_height + self.legend_margin

        return y

    def __draw_mode_representation(self, dwg, font_group, mode, x_min_mode, x_max_mode, y_start_band, mode_offset, color, str_f_min, str_f_max, text_y_pos, previous_x_max):
        """Draws the visual representation of a mode on the SVG."""
        mode_width = x_max_mode - x_min_mode

        if mode_width <= 2 or mode['id'][:7] == 'digi-ft':
            # Draw a rotated square for narrow or 'digi-ft' modes
            rect_size = (self.size_ft_square, self.size_ft_square)
            rect_pos = (x_min_mode - self.size_ft_square / 2 + mode_width / 2, y_start_band + mode_offset)
            cx = rect_pos[0] + rect_size[0] / 2
            cy = rect_pos[1] + rect_size[1] / 2
            font_group.add(dwg.rect(insert=rect_pos, size=rect_size, fill=color, transform=f"rotate(45, {cx}, {cy})"))
            font_group.add(dwg.text(str_f_min, insert=(cx, text_y_pos), font_size=self.font_size, text_anchor='middle'))
            previous_x_max = cx + rect_size[0] / 2 # Update previous_x_max for the next element
        else:
            # Draw a rectangle for wider modes
            rect_size = (mode_width, self.mode_height)
            rect_pos = (x_min_mode, y_start_band + mode_offset)
            font_group.add(dwg.rect(insert=rect_pos, size=rect_size, fill=color))

            # Determine text anchors to avoid overlap
            text_overlap_threshold = self.font_size * 0.7
            len_sum = len(str_f_min) + len(str_f_max)
            len_max = max(len(str_f_min), len(str_f_max))

            if mode_width > len_sum * text_overlap_threshold:
                text_anchor_min, text_anchor_max = ('start', 'end')
                current_x_min = x_min_mode
                current_x_max = x_max_mode
            elif mode_width > len_max * text_overlap_threshold:
                text_anchor_min, text_anchor_max = ('end', 'end')
                current_x_min = x_min_mode - (len(str_f_min) * text_overlap_threshold)
                current_x_max = x_max_mode
            else:
                text_anchor_min, text_anchor_max = ('end', 'start')
                current_x_min = x_min_mode - (len(str_f_min) * text_overlap_threshold)
                current_x_max = x_max_mode + (len(str_f_max) * text_overlap_threshold)

            # Add the minimum frequency text if it doesn't overlap the previous element
            if previous_x_max < current_x_min:
                font_group.add(dwg.text(str_f_min, insert=(x_min_mode, text_y_pos), font_size=self.font_size, text_anchor=text_anchor_min))

            # Add the maximum frequency text
            font_group.add(dwg.text(str_f_max, insert=(x_max_mode, text_y_pos), font_size=self.font_size, text_anchor=text_anchor_max))

            # Update previous_x_max based on the position and width of the maximum frequency text
            if text_anchor_max == 'end':
                previous_x_max = x_max_mode
            elif text_anchor_max == 'start':
                previous_x_max = current_x_max

        return previous_x_max

    def __draw_bands(self, font_group, dwg, y):
        """
        This function draws a band on the SVG chart.

        Args:
            bands: A dictionary containing information about the band.
            y: The y-position of the band on the chart.
        """

        mode_offset_max = 0
        for band in self.bands:
            font_group.add(dwg.line(start=(self.margin_left - 20, y), end=(self.chart_width - self.margin_right, y), stroke='black', stroke_width=1, stroke_dasharray='2,3'))
            y += 1
            font_group.add(dwg.text(band['id'], insert=(self.margin_left - 20, y + 16), fill='black', font_size=16, text_anchor='end', font_weight='bold'))
            font_group.add(dwg.text(self.__convert_frequency(band['min']) + '-' + self.__convert_frequency(band['max'], 'yes'), insert=(self.margin_left - 20, y + 28), fill='black', font_size=12, text_anchor='end'))

            y_start_band = y
            for mode in self.modes['modes']:
                color = self.mode_colors[mode['id']]
                mode_offset = {'cw': 0, 'digi': 1, 'digi-ft4': 2, 'digi-ft8': 3, 'phone': 4}[mode['id']] * (self.mode_height + self.text_height + self.mode_spacing)
                previous_x_max = 0
                for freq in mode['freq']:
                    if freq['min'] >= band['min'] and freq['max'] <= band['max']:
                        x_min_mode = self.__scale_f(freq['min'], band['min'], band['max'], self.chart_width - self.margin_right - self.margin_left) + self.margin_left
                        x_max_mode = self.__scale_f(freq['max'], band['min'], band['max'], self.chart_width - self.margin_right - self.margin_left) + self.margin_left
                        str_f_min = self.__convert_frequency(freq["min"])
                        str_f_max = self.__convert_frequency(freq["max"])
                        mode_offset_max = max(mode_offset_max, mode_offset)

                        # calculating initial positions
                        text_y_pos = y_start_band + mode_offset + self.mode_height + self.text_height

                        # check the difference betwen min and max frequencies, in order to define if print min and max or only a point
                        previous_x_max = self.__draw_mode_representation(dwg, font_group, mode, x_min_mode, x_max_mode, y_start_band, mode_offset, color, str_f_min, str_f_max, text_y_pos, previous_x_max)

            y = y_start_band + mode_offset_max + self.mode_height + self.text_height + self.band_spacing

        return y

    def create(self, filename):
        self.logger.info("Start creating bandplan svg")

        chart_height = len(self.bands) * len(self.modes["modes"]) * (self.mode_height + self.text_height + self.band_spacing + self.mode_spacing) + self.legend_height + self.margin_top + self.margin_bottom + self.footer_height

        # Create SVG drawing with responsive width and fixed height
        dwg = Drawing(filename, size=("100%", f"{chart_height}px"), viewBox=f"0 0 {self.chart_width} {chart_height}", profile='tiny')
        dwg['preserveAspectRatio'] = 'xMidYMid meet'

        # Create a group with the applied font
        font_group = dwg.g(font_family=self.font_family)

        font_group.add(dwg.rect(insert=("0%", "0%"), size=("100%", "100%"), fill='white', stroke='#f0f0f0', stroke_width=1))

        # Add centered title
        font_group.add(dwg.text(self.title, insert=("50%", f"{self.margin_top / 2}"), fill='#2F4060', font_size='24', text_anchor='middle', font_weight='bold'))

        # adding logo
        try:
            with open(self.logo_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            logo_size = 24 * 3 #same title height
            png_data_uri = f"data:image/png;base64,{encoded_string}"
            logo = dwg.image(href=png_data_uri, insert=("10%", f"{self.margin_top - logo_size / 1.5}"), size=(logo_size, logo_size))
            font_group.add(logo)
        except FileNotFoundError:
            self.logger.warning(self.logo_path + " not found!")

        y = self.margin_top

        # Dras legend
        y= self.__draw_legend(font_group,dwg,y)

        # Draw bands
        y = self.__draw_bands(font_group,dwg,y)

        # Footer with light grey background, left-aligned text and right-aligned date
        footer_height = 30  # Footer height
        footer_y = chart_height - self.margin_bottom / 3 - footer_height / 2

        font_group.add(dwg.rect(insert=(0, footer_y - footer_height / 2), size=(self.chart_width, footer_height), fill='#f0f0f0'))

        # Aggiungi il link con il testo all'interno del gruppo font_group, applicando lo stile per simulare il link
        link = dwg.a(href=self.github_link)
        text = dwg.text('IU1BOW - Spiderweb', insert=(self.margin_left, footer_y), fill='blue', font_size='12', text_anchor='start')

        # Aggiungi il testo come parte del link
        link.add(text)

        # Aggiungi il gruppo di link al font_group
        font_group.add(link)

        font_group.add(dwg.text(date.today().strftime("%d/%m/%Y"), insert=(self.chart_width - self.margin_right, footer_y), fill='black', font_size='12', text_anchor='end'))

        # Add group to drawing
        dwg.add(font_group)


        # Save the SVG file
        try:
            dwg.save()
            self.logger.info("bandplan svg created in: %s", filename)
        except Exception as e:
            self.logger.error(e)