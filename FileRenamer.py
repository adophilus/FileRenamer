import os
import re

class FileRenamer ():
	def __init__ (self, path, match_criteria, renaming_system = "{match_criteria} {season_prefix} {season_number} {episode_prefix} {episode_number}.{renaming_extension}", season_match_criteria = "", season_max_length = 3, season_filler = "0", season_prefix = "season", episode_match_criteria = "\\d", epsiode_max_length = 3, episode_filler = "0", episode_prefix = "episode", renaming_extension = "{original_extension}", strip_preceding_zeros = True):
		self.path = path
		self.match_criteria = re.compile(match_criteria)
		self.renaming_system = renaming_system
		self.season_match_criteria = re.compile(season_match_criteria)
		self.season_prefix = season_prefix
		self.season_max_length = season_max_length
		self.season_filler = season_filler[:1]
		self.episode_match_criteria = re.compile(episode_match_criteria)
		self.episode_prefix = episode_prefix
		self.episode_max_length = epsiode_max_length
		self.episode_filler = episode_filler[:1]
		self.renaming_extension = renaming_extension
		self.strip_preceding_zeros = strip_preceding_zeros

		self.messages = {
			"error": {
				"INVALID_PATH": "The path specified is invalid!"
			},
			"success": {

			}
		}
	def check_path (self):
		return (os.path.isdir(self.path))

	def check_match_criteria (self, file_name):
		return bool(self.match_criteria.search(file_name))

	def check_season_match_criteria(self, file_name):
		return (bool(self.season_match_criteria.search(file_name))
		        if self.season_match_criteria.pattern else True)

	def check_episode_match_criteria (self, file_name):
		return bool(self.episode_match_criteria.search(file_name))

	def is_match_season_enabled (self):
		return (self.season_match_criteria.pattern == True)

	def get_season_number(self, file_name):
		match = self.season_match_criteria.search(file_name)
		if not match:
			return False
		season_number_match = re.compile("\\d+").search(match.group())
		# print(season_number_match)
		if not season_number_match:
			return False
		if season_number := season_number_match.group():
			if self.strip_preceding_zeros:
				season_number = re.compile("^0+").sub("", season_number)
			if len(season_number) < self.season_max_length:
				length_remaining = self.season_max_length - len(season_number)
				filler = self.season_filler * length_remaining
				season_number = self.fill_season_number(filler, season_number)
			return season_number

	def get_episode_number(self, file_name):
		match = self.episode_match_criteria.search(file_name)
		if not match:
			return False
		episode_number_match = re.compile("\\d+").search(match.group())
		if not episode_number_match:
			return False
		if episode_number := episode_number_match.group():
			if self.strip_preceding_zeros:
				episode_number = re.compile("^0+").sub("", episode_number)
			if len(episode_number) < self.episode_max_length:
				length_remaining = self.episode_max_length - len(episode_number)
				filler = self.episode_filler * length_remaining
				episode_number = self.fill_episode_number(filler, episode_number)
			return episode_number

	def fill_episode_number (self, fill, episode_number):
		return f"{fill}{episode_number}"

	def fill_season_number (self, fill, season_number):
		return f"{fill}{season_number}"

	def get_crude_match(self, file_name):
		st = [file_name, self.check_match_criteria(file_name)]
		st.append(self.check_season_match_criteria(file_name))
		st.append(self.check_episode_match_criteria(file_name))
		return st

	def get_processed_match(self, file_name, match_criteria, match_season_criteria, match_episode_criteria):
		if not match_criteria:
			return
		season_number = self.get_season_number(file_name)
		episode_number = self.get_episode_number(file_name)
		if not (episode_number):
			return
		return [file_name, season_number, episode_number]

	def refine_processed_list(self, processed_list):
		# The following lines would remove any useless data from the refined list
		count = processed_list.count(None)
		for _ in range(count):
			processed_list.remove(None)
		return processed_list

	def __get_renaming_list(self, file_name, season_number, episode_number):
		original_extension = re.compile("^\\.+").sub("", file_name).split(".")
		original_extension = ".".join(original_extension[1:])
		return [
		    file_name,
		    self.renaming_system.format(
		        match_criteria=self.match_criteria,
		        season_prefix=self.season_prefix,
		        season_number=season_number,
		        episode_prefix=self.episode_prefix,
		        episode_number=episode_number,
		        renaming_extension=self.renaming_extension.format(
		            original_extension=original_extension),
		        original_extension=original_extension,
		    ),
		]

	def get_renaming_list(self):
		if not (self.check_path()):
			return [False, self.messages["error"]["INVALID_PATH"]]

		list_of_files = os.listdir(self.path)
		matching_files = {
		    "crude": [self.get_crude_match(file_name) for file_name in list_of_files]
		}
		matching_files["processed"] = [self.get_processed_match(file_name, match_criteria, match_season_criteria, match_episode_criteria) for file_name, match_criteria, match_season_criteria, match_episode_criteria in matching_files["crude"]]
		matching_files["refined"] = self.refine_processed_list(matching_files["processed"])

		[print(record) for record in matching_files["crude"]]
		return [
		    self.__get_renaming_list(file_name, season_number, episode_number)
		    for file_name, season_number, episode_number in matching_files["refined"]
		]

	def rename_files_with_list (self, renaming_list, destination_path = "{path}", rename = True):
		destination_path = destination_path.format(path = self.path)
		return_list = []
		for old_name, new_name in renaming_list:
			file_name_diff = [old_name, os.path.abspath(os.path.join(destination_path, new_name))]
			if rename:
				os.rename(*file_name_diff)
			return_list.append(file_name_diff)
		return return_list

if __name__ == "__main__":
	renamer = FileRenamer(path = ".", match_criteria = "mha", renaming_system = "My Hero Academia {season_prefix} {season_number} {episode_prefix} {episode_number}.mp4", episode_match_criteria = "ep\\s\\d", season_match_criteria = "s\\s\\d", season_filler = "", episode_filler = "", strip_preceding_zeros = True)
	renaming_list = renamer.get_renaming_list()
	renamed_list = renamer.rename_files_with_list(renaming_list, rename = 1)
	print(renamed_list)