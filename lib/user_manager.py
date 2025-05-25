# lib/user_manager.py
import fcntl
import os
import time
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

logger = logging.getLogger(__name__)

# User file in the format: username:profile:hashed_password:must_change_password (boolean as 0 or 1)
USER_DB_FILE = 'local/data/users.txt' 

class User(UserMixin):
    def __init__(self, id, username, password_hash, profile, must_change_password=False):
        self.id = id # Corresponds to username for simplicity
        self.username = username
        self.password_hash = password_hash
        self.profile = profile
        # The 'is_active' property is handled by UserMixin and should not be set directly.
        self.must_change_password = must_change_password

    def get_id(self):
        return str(self.id)

    # This method is now only for internal logic, not for file writing in this format
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'profile': self.profile,
            'must_change_password': self.must_change_password
        }

class UserManager:
    def __init__(self):
        self._ensure_user_file_exists()

    def _ensure_user_file_exists(self):
        """Ensures the user file exists."""
        if not os.path.exists(USER_DB_FILE):
            logger.info(f"User file not found at {USER_DB_FILE}. Creating it.")
            try:
                # Create an empty file if it doesn't exist
                with open(USER_DB_FILE, 'w') as f:
                    pass
            except Exception as e:
                logger.error(f"Error creating user file: {e}")
                raise

    def _acquire_file_lock(self, f):
        """Attempts to acquire an exclusive lock on the file without blocking."""
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB) # LOCK_NB for non-blocking
            return True
        except BlockingIOError:
            return False # Lock not available
        except Exception as e:
            logger.error(f"Unexpected error acquiring lock: {e}")
            return False

    def _release_file_lock(self, f):
        """Releases the lock on the file."""
        fcntl.flock(f, fcntl.LOCK_UN)

    def _read_users_from_file(self, max_retries=10, delay_seconds=0.05):
        """Reads all users from the file with retry and lock management, in user:profile:hash:must_change_password format."""
        for attempt in range(max_retries):
            try:
                # Open in r+ mode to be able to seek(0) and truncate after reading if necessary
                with open(USER_DB_FILE, 'r+') as f: 
                    if self._acquire_file_lock(f):
                        users = {}
                        try:
                            f.seek(0) # Ensure reading from the beginning
                            for line in f:
                                line = line.strip()
                                if line:
                                    # --- START CORRECTION HERE ---
                                    # Split by the LAST colon to get the must_change_password flag
                                    # This assumes the must_change_password flag is always the last part
                                    main_data, must_change_str = line.rsplit(':', 1)
                                    must_change_password = True if must_change_str == '1' else False
                                    
                                    # Now split the main_data by the FIRST TWO colons
                                    # This correctly separates username, profile, and the full hashed_password
                                    parts = main_data.split(':', 2)
                                    
                                    if len(parts) == 3: # Expecting username, profile, hashed_password
                                        username, profile, hashed_password = parts
                                        users[username] = User(username, username, hashed_password, profile, must_change_password)
                                    else:
                                        logger.warning(f"Malformed line in user file after rsplit: {line}")
                                    # --- END CORRECTION HERE ---
                            return users
                        except Exception as e:
                            logger.error(f"Error reading user file content (attempt {attempt + 1}): {e}")
                            raise # Re-raise to handle the error after finally
                        finally:
                            self._release_file_lock(f)
                    else:
                        logger.debug(f"Lock not available for reading, retrying... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay_seconds)
            except FileNotFoundError:
                logger.warning(f"User file {USER_DB_FILE} not found during read (attempt {attempt + 1}).")
                self._ensure_user_file_exists() # Attempt to recreate it
                time.sleep(delay_seconds)
            except Exception as e:
                logger.error(f"Generic error during user file read (attempt {attempt + 1}): {e}")
                time.sleep(delay_seconds)
        logger.critical(f"Failed to read user file after {max_retries} attempts.")
        return {} # Return an empty dictionary if it fails after all attempts

    def _write_users_to_file(self, users_dict, max_retries=10, delay_seconds=0.05):
        """Writes all users to the file with retry and lock management, in user:profile:hash:must_change_password format."""
        for attempt in range(max_retries):
            try:
                # Open in w+ mode to truncate and write from the beginning
                with open(USER_DB_FILE, 'w+') as f: 
                    if self._acquire_file_lock(f):
                        try:
                            for username, user in users_dict.items():
                                must_change_str = '1' if user.must_change_password else '0'
                                f.write(f"{user.username}:{user.profile}:{user.password_hash}:{must_change_str}\n")
                            # Important to remove residual data if the new content is shorter
                            f.truncate() 
                            return True
                        except Exception as e:
                            logger.error(f"Error during actual data writing (attempt {attempt + 1}): {e}")
                            raise
                        finally:
                            self._release_file_lock(f)
                    else:
                        logger.debug(f"Lock not available for writing, retrying... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay_seconds)
            except Exception as e:
                logger.error(f"Generic error during file write operation (attempt {attempt + 1}): {e}")
                time.sleep(delay_seconds)
        logger.critical(f"Failed to write user file after {max_retries} attempts.")
        return False

    def get_user_by_id(self, user_id):
        # ID and username are the same for simplicity in this implementation
        return self.get_user_by_username(user_id) 

    def get_user_by_username(self, username):
        users = self._read_users_from_file()
        return users.get(username)

    def add_user(self, username, password, profile="user", must_change_password=False):
        users = self._read_users_from_file()
        if username in users:
            logger.warning(f"Attempt to add existing user: {username}")
            return False, "User already exists."
        
        hashed_password = generate_password_hash(password)
        new_user = User(username, username, hashed_password, profile, must_change_password)
        users[username] = new_user

        if self._write_users_to_file(users):
            logger.info(f"User '{username}' added successfully.")
            return True, "User added successfully."
        else:
            logger.error(f"Failed to add user '{username}'.")
            return False, "Error adding user."

    def verify_user(self, username, password):
        users = self._read_users_from_file()
        user = users.get(username)
        if user and check_password_hash(user.password_hash, password):
            logger.info(f"Login successful for user: {username}")
            return user
        logger.warning(f"Login attempt failed for user: {username}")
        return None

    def update_user_password(self, username, new_password, set_must_change_false=True):
        users = self._read_users_from_file()
        user = users.get(username)
        if not user:
            logger.warning(f"Attempt to change password for non-existent user: {username}")
            return False, "User not found."

        user.password_hash = generate_password_hash(new_password)
        if set_must_change_false:
            user.must_change_password = False # Reset the flag after password change

        if self._write_users_to_file(users):
            logger.info(f"Password for user '{username}' updated successfully.")
            return True, "Password updated successfully."
        else:
            logger.error(f"Failed to update password for user '{username}'.")
            return False, "Error updating password."

    def update_user_profile(self, username, new_profile):
        users = self._read_users_from_file()
        user = users.get(username)
        if not user:
            logger.warning(f"Attempt to change profile for non-existent user: {username}")
            return False, "User not found."
        
        user.profile = new_profile

        if self._write_users_to_file(users):
            logger.info(f"Profile for user '{username}' updated successfully to '{new_profile}'.")
            return True, "Profile updated successfully."
        else:
            logger.error(f"Failed to update profile for user '{username}'.")
            return False, "Error updating profile."

    def delete_user(self, username):
        users = self._read_users_from_file()
        if username not in users:
            logger.warning(f"Attempt to delete non-existent user: {username}")
            return False, "User not found."
        
        del users[username]
        if self._write_users_to_file(users):
            logger.info(f"User '{username}' deleted successfully.")
            return True, "User deleted successfully."
        else:
            logger.error(f"Failed to delete user '{username}'.")
            return False, "Error deleting user."

    def get_all_users(self):
        return list(self._read_users_from_file().values())