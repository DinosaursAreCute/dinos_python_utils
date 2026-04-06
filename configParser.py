from Utils import Logger,osHelper
import logic.fileOperations as fop
import yaml
import re
import colorama as color 
class configParser():
    log = Logger.LoggerClass(0,"config_parser")
    variables=["AUTO_IP","USER"]
    
    def __init__(self,config_file_path: str,base_directory: str = '.'):
        try:
            self.config_file_path = fop.convert_string_to_path(config_file_path)
            self.base_directory   = fop.convert_string_to_path(base_directory)
            
            self.log.value(f"Using configuration found at: {config_file_path}")
            self.log.value(f"Using base directory at: {base_directory}")
            
            if not fop.check_file_exists(self.config_file_path):
                self.log.fatal(f"Config file: '{self.config_file_path}' not found.")
                raise IOError
            try:
                self.config_file = fop.read_file(file_path=self.config_file_path,strip=True,enumerate=True)
            except Exception as e:
                self.log.fatal(f"Failed to read config file: '{config_file_path}'")
                raise e
        
            self.config_file = self.parse_config(config_file=self.config_file,debug=False)
            self.config_file = self.replace_variables(config_file=self.config_file,debug=False)
            self.line_config_values,self.category_config_values,self.loaded_files = self.get_config_values(debug=False)
        except Exception as e:
            self.log.fatal(f"Unexpected Error occured during config parser initialization. {e}")
            raise e
        
    def parse_config(self,config_file:dict,debug: bool = False):
    # removes comments and empty lines from content list 
    # args:
    #   debug : bool --> If true verbose logging is enabled 
        rmCache=[]  
        for line_number,line_content in config_file.items():
            if line_content == "":
                rmCache.append(line_number)
                continue
            if line_content[0]=='#':
                rmCache.append(line_number)
        for key in rmCache:
            config_file.pop(key)        
        if debug: self.log.debug(config_file)  
        return config_file     
             
   
    def get_config_values(self, debug: bool = False):
        """
        Build two dicts:

        line_entries:
            {
                filename: {
                    line_number: content_str,
                    ...
                },
                ...
            }

        category_entries:
            {
                filename: {
                    category: [content_str, content_str, ...],
                    ...
                },
                ...
            }
        """
        line_entries = {}
        category_entries = {}
        loaded_files={}
        
        for line_key, content in self.config_file.items():
            parts = content.split(":", 2)
            if debug:
                self.log.debug(f"Parts for line_key={line_key!r}: {parts!r}")

            if len(parts) < 3:
                if debug:
                    self.log.debug(f"Skipping malformed config line {line_key!r}: {content!r}")
                continue

            filename = parts[0].strip()
            second = parts[1].strip()      # line number OR category
            rest = parts[2].strip()        # the remaining content


            # --- Loading files content --- 
            if not filename in loaded_files:
                    file_content=fop.read_file(file_path=f"{self.base_directory}/{filename}",strip=True,enumerate=True)
                    if file_content == None:
                        file_content={0:''}
                    loaded_files[filename]=file_content
            # --- line-based entries ---
            try:
                line_no = int(second)
                if filename in line_entries and line_no in line_entries[filename]:
                    self.log.warning(f"Skipping duplicate config entry for '{filename}' line: '{line_no}' ")
                    continue
                file_lines = line_entries.setdefault(filename, {})
                file_lines[line_no] = rest
                continue
            except ValueError:
                pass  # not a number → treat as category

            # --- category-based entries ---
            category = second
            file_cats = category_entries.setdefault(filename, {})
            file_cats.setdefault(category, []).append(rest)

        if debug:
            print("\nLine-based entries:")
            for filename, lines in line_entries.items():
                print(f"File: {filename}")
                for ln, cnt in sorted(lines.items()):
                    print(f"  {ln}: {cnt}")

            print("\nCategory-based entries:")
            for filename, cats in category_entries.items():
                print(f"File: {filename}")
                for cat, contents in cats.items():
                    for c in contents:
                        print(f"  [{cat}] {c}")

        return line_entries, category_entries,loaded_files

    def replace_variables(self,config_file:dict,debug: bool = False):
        if debug: self.log.debug("replace_variable was called")
        for line,content in config_file.items():
            temp_content = content
            _content = content.split(':', maxsplit=2)[2]
            if re.search(r"<.*>", _content):
                variable = re.search(r"<(.*)>", _content)
                if debug: self.log.debug(f"Found a variable:'{variable.group(1)}'.")
                match variable.group(1):
                    case "AUTO_IP":
                        content = re.sub(r"<AUTO_IP>", osHelper.get_active_hostname(), content)
                        if debug:
                            self.log.debug(f"replaced <AUTO_IP> with {osHelper.get_active_hostname}")
                            self.log.debug(f"{temp_content} --> {content}")
                    case "USER":
                        self.log.warning("<USER> variable not yet implemented")
            config_file[line]=content
            if debug: self.log.debug(content)
            return config_file
    
    def get_yaml_value(self, data, key, category=None, default=None):
        """
        Recursively search `data` for a dict under `category`, then return
        the value of `key` from that dict. If not found, return `default`.

        :param data:     dict (or nested dict/list) loaded from YAML
        :param key:      key to find the value of
        :param category: name of the dict key to search for (e.g. 'healthcheck');
                        if None, search at top level only
        :param default:  value to return if key/category not found
        :return:         key,value or key,default
        """
        self.log.debug(f"get_yaml_value: key={key}, category={category}, default={default}")

        # If no category is given, just use the top-level dict
        if category is None:
            if not isinstance(data, dict):
                return default
            return data.get(key, default)

        # Helper: recursively find the first dict under the given category key
        def find_category(node):
            # If this node is a dict, check for the category key
            if isinstance(node, dict):
                if category in node and isinstance(node[category], dict):
                    return node[category]

                # Otherwise, recurse into all values
                for v in node.values():
                    found = find_category(v)
                    if found is not None:
                        return found

            # If this node is a list, recurse into each element
            elif isinstance(node, list):
                for item in node:
                    found = find_category(item)
                    if found is not None:
                        return found

            # Anything else: no match here
            return None

        category_dict = find_category(data)

        if category_dict is None:
            self.log.debug(f"Category '{category}' not found; returning default")
            return default

        self.log.debug(f"Category '{category}' found; extracting key '{key}'")
        return category_dict.get(key, default)

    def find_line_based_mismatches(self,line_config_values:dict,log_result:bool=True,debug:bool=False):
        mismatches=[]
        lines_to_check=line_config_values
        matches=0
        try:
            for file,values in lines_to_check.items():
                file_path = f"{self.base_directory}/{file}"
                if debug: self.log.debug(f"Checking file:{f"{file}"}. Exists={fop.check_file_exists(f"{file_path}")}")
                if not file in self.loaded_files: 
                    self.log.warning(f"File: {file} not in loaded files. Skipping")
                    continue
                
                for line,line_value in values.items():
                    if not fop.check_file_exists(f"{file_path}"):
                        self.log.error(f"File: '{file_path}' not found. line: {line}, expected: {line_value}, actual: None")
                        mismatches.append(
                            {
                                "filename": file,
                                "category": "line",
                                "key": line,
                                "expected": line_value,
                                "actual": None,
                            }  
                        )
                        continue
                    if debug: self.log.debug(f"Checking '{file}, line: {line} for content:{line_value}")
                    expected=line_value
                    if len(self.loaded_files[file]) < line-1:
                        actual=""
                    else:    
                        actual=self.loaded_files[file][line-1]
                    if not actual == expected:
                        self.log.error(f"Mismatch in '{file}' at line {line}. Expected:'{expected}' but found: '{actual}'")
                        mismatches.append(
                            {
                                "filename": file,
                                "category": "line",
                                "key": line,
                                "expected": expected,
                                "actual": actual,
                            }  
                        )
                    else: 
                        self.log.success(f"Match   in  '{file}' at line {line}. Found   :'{actual}'")
                        matches+=1
        except KeyError as k:
            self.log.fatal(f"Caught key error. {file,line,line_value}")
            try: 
                self.log.fatal(f"Error Occured due to maleformed data. Raw Data: {self.loaded_files[file]}")
            except KeyError as k1:
                self.log.fatal(f"Key Error occured due to unloaded file:{file}")
            raise k
        except AttributeError as e:
            self.log.fatal(f"Caught Attribute error. Data={lines_to_check}")
            raise e 
            
        if log_result: 
            
            print("\n")
            self.log.info(f"{color.Fore.LIGHTGREEN_EX+color.Style.BRIGHT+color.Back.BLACK}----- MISMATCHES ({matches}) ----- {color.Style.RESET_ALL}")
            self.log.info(f"{color.Fore.LIGHTYELLOW_EX+color.Style.BRIGHT+color.Back.BLACK}----- MISMATCHES ({len(mismatches)}) ----- {color.Style.RESET_ALL}")
            for mismatch in mismatches:
                self.log.error(f"{color.Fore.LIGHTYELLOW_EX+color.Style.NORMAL+color.Back.BLACK}File:'{mismatch["filename"]}', line:{mismatch["key"]}, expected:'{mismatch["expected"]}', actual:'{mismatch["actual"]}'{color.Style.RESET_ALL}")
            
        return mismatches
        
        
    def find_yaml_mismatches(self, category_entries, yaml_data,debug:bool = False):
        """
        Compare expected values from category_entries with actual values in yaml_data.

        Args:
            category_entries: dict
                {
                    filename: {
                        category: [ "key: value # comment", ... ],
                        ...
                    },
                    ...
                }
            yaml_data: dict
                Parsed YAML (the structure to search in).

        Returns:
            list of dicts, each mismatch like:
            {
                "filename":  <str>,
                "category":  <str>,
                "key":       <str>,
                "expected":  <str>,
                "actual":    <any>,
            }
        """
        mismatches = []
        logger = self.log

        for filename, categories in category_entries.items():
            if not filename.lower().endswith((".yml", ".yaml")):
                continue

            if debug: logger.debug(f"Processing config for YAML file: {filename}")

            # categories: { category: [raw1, raw2, ...], ... }
            for category, raw_list in categories.items():
                for raw in raw_list:
                    # raw is like "key: value # comment"
                    try:
                        key_part, rest = raw.split(":", maxsplit=1)
                    except ValueError:
                        if debug: logger.debug(f"Skipping malformed entry (no colon): {raw!r}")
                        continue

                    key_part = key_part.strip()
                    value_part = rest.split("#", maxsplit=1)[0].strip()

                    if debug: logger.debug(
                        f"Search in filename='{filename}': "
                        f"category='{category}', key='{key_part}', expected='{value_part}'"
                    )

                    # Look up actual value in YAML
                    actual = self.get_yaml_value(
                        yaml_data,
                        key=key_part,
                        category=category,
                        default=None,
                    )

                    if str(actual) != value_part:
                        print(f"{actual} != {value_part}")
                        if debug: logger.debug(
                            f"Mismatch for {filename} / {category} / {key_part}: "
                            f"actual={actual!r}, expected={value_part!r}"
                        )
                        mismatches.append(
                            {
                                "filename": filename,
                                "category": category,
                                "key": key_part,
                                "expected": value_part,
                                "actual": actual,
                            }
                        )
                    else:
                        if debug: print(f"Result: {actual} = {value_part}")
                        if debug: logger.debug(
                            f"Match for {filename} / {category} / {key_part}: "
                            f"value={actual!r}"
                        )

        return mismatches

    def _find_category_path(self, node, category):
        """
        Recursively search `node` for a dict under `category` and return
        the path to that dict as a list of keys/indexes.

        Example return: ['services', 'lsh', 'healthcheck']

        Returns None if not found.
        """
        # If this node is a dict, check for the category key
        if isinstance(node, dict):
            if category in node and isinstance(node[category], dict):
                return [category]

            # Otherwise, recurse into all values
            for k, v in node.items():
                sub_path = self._find_category_path(v, category)
                if sub_path is not None:
                    return [k] + sub_path

        # If this node is a list, recurse into each element
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                sub_path = self._find_category_path(item, category)
                if sub_path is not None:
                    return [idx] + sub_path

        # Anything else: no match here
        return None




    def _get_by_path(self, node, path):
        """
        Follow `path` (list of keys/indexes) into `node` and return the final object.
        Returns None if any step is invalid.
        """
        current = node
        for p in path:
            if isinstance(current, dict) and p in current:
                current = current[p]
            elif isinstance(current, list) and isinstance(p, int) and 0 <= p < len(current):
                current = current[p]
            else:
                return None
        return current




    def prettyPrint_yaml(self,data:any):
        return yaml.safe_dump(
            data,
            sort_keys=False,   # keep original key order
            default_flow_style=False,  # block style, not inline
            indent=2
        )
        
    def update_lines(self,lines_to_change:dict,debug:bool=False):
        if debug: self.log.debug(f"Lines to update: {lines_to_change}")
        buffer=self.loaded_files.copy()
        try:
            for entry in lines_to_change:
                self.log.info(f"Updating:{entry}")
                buffer[entry["filename"]][entry["key"]]=entry["expected"]
                real_line=self.loaded_files[entry["Filename"]][entry["key"]]
        except KeyError:
            pass
        if debug: self.log.debug(f"Buffered:{buffer}")
        self.find_line_based_mismatches(line_config_values=self.line_config_values,log_result=True)
        for key, value in buffer.items():
            filepath=f"{self.base_directory}/{key}"
            self.log.info(f"Writing data to: {filepath}")
            fop.write_to_file(filepath,value,True)
            self.log.info(f"Reading new data from: {filepath}")
            self.loaded_files[key]=fop.read_file(f"{self.base_directory}/{key}",strip=True,enumerate=True)
        #self.loaded_files = self.reload_files(self.loaded_files)
    
    
    def reload_files(self,files_to_update:dict,debug:bool=False):
        files={}
        
        for key in files_to_update.keys():
            filepath=f"{self.base_directory}/{key}"
            self.log.info(f"Reading file: {key} at {filepath}")
            files[key]=fop.read_file(file_path=filepath,strip=True,enumerate=True)
        return files