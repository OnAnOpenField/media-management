#include "SubFilter.h"

#define INI_FILEPATH "config.ini"

// remove subtitle credits and strip font color tags
bool filterSubfile(const std::string &subFilename, const std::vector<std::string> & creditslist, std::ofstream & wLogfile) {
	std::vector<std::vector<std::string>> toProceedBoolList;
	std::vector<std::string> subfileContents;
	std::vector<std::vector<std::string>> newSubfileContents;
	std::string sTemp;

	//open sub file for reading
	std::ifstream rSubfile(subFilename);
	if (!rSubfile.good()) {
		std::cout << "'" << subFilename << "' could not be opened for reading\n";
		wLogfile << "'" << subFilename << "' could not be opened for reading\n";
		return 0;
	}

	//read from sub file
	while (std::getline(rSubfile, sTemp)) {
		if (isFullyEmpty(sTemp)) {
			continue;
		}
		subfileContents.push_back(sTemp);
	}
	rSubfile.close();

	toProceedBoolList = {
		{ "hasSDH", "0" }, 
		{ "hasColorTags", "0" }, 
		{ "hasCredits", "0" }
	};
	
	isSubfileDirty(toProceedBoolList, creditslist, subfileContents);
	bool subfileHasTextForHI = (toProceedBoolList[0][1] == "1");
	bool subfileisColorTagged = (toProceedBoolList[0][1] == "1");
	bool subfileHasCredits = (toProceedBoolList[2][1] == "1");

	//check if subs are dirty or have color tags
	if (!subfileHasCredits && !subfileisColorTagged && !subfileHasTextForHI) {
		return 0;
	}

	//open sub file for writing
	std::ofstream wSubfile(subFilename, std::ios::trunc);
	if (!wSubfile.good()) {
		std::cerr << "'" << subFilename << "' could not be opened for writing\n";
		return 0;
	}

	cout << "Filtering '" << subFilename << "'\n\n";
	wLogfile << "Filtering '" << subFilename << "'\n\n";
	
	// keep track of line number that is being filtered/edited
	int lineNum = 1;
	std::vector<std::string> subblock;
	std::vector<std::string> subblock_old;
	
	// filter sub file and remove color tags
	for (int i = 0; i < subfileContents.size() - 1; ++i) {
		// if is not sub line number, ie. not start of sub block
		if (!isTimeStamp(subfileContents[i + 1])) {
			subblock.push_back(subfileContents[i]);
		}

		// if sub block has ended
		if (!subblock.empty() && isTimeStamp(subfileContents[i + 1]) || i + 2 >= subfileContents.size()) {
			if (i + 2 >= subfileContents.size()) {
				subblock.push_back(subfileContents[i + 1]);
			}

			// if sub block contains credits
			if (subfileHasCredits && hasCredits(creditslist, subblock)) {
				cout << "    Line " << lineNum << " filtered:\n";
				wLogfile << "    Line " << lineNum << " filtered:\n";

				for (int k = 1; k < subblock.size(); ++k) {
					cout << "    >>   " << subblock[k] << "\n";
					wLogfile << "    >>   " << subblock[k] << "\n";
				}
				cout << "\n";
				wLogfile << "\n";

				subblock.clear();
			}

			if (subfileHasTextForHI && hasTextForHI(subblock) && !subblock.empty()) {
				cout << "    Line " << lineNum << " text for HI removed.\n\n";
				wLogfile << "    Line " << lineNum << " text for HI removed.\n\n";

				removeTextForHI(subblock);
				removeEmptySubLines(subblock);
				trim(subblock);
			}

			// if sub block is color tagged
			if (subfileisColorTagged && isColorTagged(subblock) && !subblock.empty()) {
				for (int k = 0; k < subblock.size(); ++k) {
					subblock_old.push_back(subblock[k]);
				}

				cout << "    Line " << lineNum << " color tags removed:\n";
				wLogfile << "    Line " << lineNum << " color tags removed:\n";
				removeFontTags(subblock);

				for (int k = 1; k < subblock.size(); ++k) {
					cout << "    >>   " << subblock_old[k] << " --> " << subblock[k] << "\n";
					wLogfile << "    >>   " << subblock_old[k] << " --> " << subblock[k] << "\n";
				}
				cout << "\n";
				wLogfile << "\n";

				removeEmptySubLines(subblock);
				subblock_old.clear();
			}

			// write clean subs to subtitle-block vector
			if (!subblock.empty()) {
				newSubfileContents.push_back(subblock);
			}
			subblock.clear();
			++lineNum;
		}
	}
	
	int wLineNum = 1;
	// write clean subs back to subtitle file
	for (int i = 0; i < newSubfileContents.size(); ++i) {
		wSubfile << wLineNum << "\n";
		for (int k = 0; k < newSubfileContents[i].size(); ++k) {
			wSubfile << newSubfileContents[i][k] << "\n";
		}
		wSubfile << "\n";
		++wLineNum;
	}
	

	return 1;
}

std::string getIniValue(const std::string & iniKey) {
	std::ifstream rIniFile(INI_FILEPATH);
	if (!rIniFile.good()) {
		cout << "\"config.ini\" not found. Press Enter to continue.\n";
		cin.get();
		exit(1);
	}

	std::string sTemp;

	while (std::getline(rIniFile, sTemp)) {
		if (sTemp.find(iniKey) == 0) {
			for (int i = iniKey.size(); i < sTemp.size(); ++i) {
				if (!isspace(sTemp[i]) && sTemp[i] != '=') {
					return sTemp.substr(i, sTemp.size() - 1);
				}
			}
		}
	}

	fatal(iniKey + " key not found in config.ini");
}

// get Season and Episode string from title. Some subtitles add the title to the subtitles and are usually followed by advertisements.
std::string getEpisodeStr(const std::string & subFilename) {
	std::smatch sm;
	std::regex e("s[0-9][0-9]e[0-9][0-9]", std::regex_constants::icase);
	std::regex_search(subFilename, sm, e);

	return sm[0];
}

// test if subtitles need filtering
void isSubfileDirty(std::vector <std::vector <std::string>> & toProceedBoolList, const std::vector<std::string> & creditslist, std::vector<std::string> subfileContents) {
	for (int i = 0; i < subfileContents.size(); ++i) {
		if (subfileContents[i].find('[') != std::string::npos) {
			toProceedBoolList[0][1] = "1";
			break;
		}
	}
	
	std::string sTemp;
	for (int i = 0; i < subfileContents.size(); ++i) {
		sTemp = subfileContents[i];
		std::transform(sTemp.begin(), sTemp.end(), sTemp.begin(), ::tolower);
		if (sTemp.find('<') != std::string::npos && sTemp.find("font") != std::string::npos && sTemp.find('=') != std::string::npos) {
			toProceedBoolList[1][1] = "1";
			break;
		}
	}
	
	for (int i = 0; i<creditslist.size(); ++i) {
		for (int k = 0; k<subfileContents.size(); ++k) {
			std::regex e(creditslist[i], std::regex_constants::icase);
			if (regex_search(subfileContents[k], e)) {
				toProceedBoolList[2][1] = "1";
				return;
			}
		}
	}	
}

bool hasTextForHI(const std::vector <std::string> subblock) {
	for (int i = 0; i < subblock.size(); ++i) {
		if (subblock[i].find('[') != std::string::npos) {
			return true;
		}
	}

	return false;
}

void removeTextForHI(std::vector <std::string> & subblock) {
	for (int i = 1; i<subblock.size(); ++i) {
		while (subblock[i].find('[') != std::string::npos && subblock[i].find(']') != std::string::npos) {
			subblock[i].erase(subblock[i].begin() + subblock[i].find('['), subblock[i].begin() + subblock[i].find(']') + 1);
		}
		if (subblock[i].find('[') != std::string::npos && subblock[i].find(']') == std::string::npos) {
			subblock[i].erase(subblock[i].begin() + subblock[i].find('['), subblock[i].end());
			for (++i; i<subblock.size() && subblock[i].find(']') == std::string::npos; ++i) {
				subblock[i].erase(subblock[i].begin(), subblock[i].end());
			}
			subblock[i].erase(subblock[i].begin(), subblock[i].begin() + subblock[i].find(']') + 1);
		}
	}
}

bool isColorTagged(const std::vector<std::string> & subblock) {
	std::string sTemp;
	for (int i = 0; i < subblock.size(); ++i) {
		sTemp = subblock[i];
		std::transform(sTemp.begin(), sTemp.end(), sTemp.begin(), ::tolower);
		if (sTemp.find('<') != std::string::npos && sTemp.find("font") != std::string::npos && sTemp.find('=') != std::string::npos) {
			return true;
		}
	}

	return false;
}

void removeFontTags(std::vector <std::string> & subblock) {
	fixTags(subblock);
	std::string sTemp;

	for (int i = 0; i < subblock.size(); ++i) {
		sTemp = subblock[i];
		std::transform(sTemp.begin(), sTemp.end(), sTemp.begin(), ::tolower);

		for (int k = sTemp.find("<font"), n = sTemp.find("<font"); k < sTemp.size(); ++k) {
			if (sTemp[k] == '>') {
				subblock[i].erase(n, k - n + 1);
				break;
			}
		}

		sTemp = subblock[i];
		for (int k = sTemp.find("</font"), n = sTemp.find("</font"); k < sTemp.size(); ++k) {
			if (sTemp[k] == '>') {
				subblock[i].erase(n, k - n + 1);
				break;
			}
		}
	}
}

// remove extraneous whitespace from tags.
void fixTags(std::vector<std::string> & subblock) {
	for (int i = 1; i < subblock.size(); ++i) {
		for (int k = 0; k < subblock[i].size(); ++k) {
			if (subblock[i][k] == '<') {
				for (; subblock[i][k] != '>' && k < subblock[i].size(); ++k) {
					while (isspace(subblock[i][k])) {
						subblock[i].erase(subblock[i].begin() + k);
					}
				}
			}
		}
	}
}

inline bool hasCredits(const std::vector <std::string> & creditslist, std::vector<std::string> subblock) {
	for (int i = 0; i<creditslist.size(); ++i) {
		for (int k = 0; k<subblock.size(); ++k) {
			std::regex e(creditslist[i], std::regex_constants::icase);
			if (regex_search(subblock[k], e)) {
				return true;
			}
		}
	}

	return false;
}

void removeEmptySubLines(std::vector <std::string> & subblock) {
	for (int i = 0; i < subblock.size(); ++i) {
		while (i < subblock.size() && isFullyEmpty(subblock[i])) {
			subblock.erase(subblock.begin() + i);
		}
	}

	if (subblock.size() == 1) {
		subblock.clear();
	}
}

inline bool isTimeStamp(const std::string & sTest) {
	std::regex e("[0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9]");
	return regex_search(sTest, e);
}

void trim(std::vector <std::string> & subblock) {
	for (int i = 1; i<subblock.size(); ++i) {
		int start = -1;
		int end = -1;
		for (int k = 0; k < subblock[i].size() && start == -1; ++k) {
			if (!isspace(subblock[i][k])) {
				start = k;
			}
		}

		for (int k = subblock[i].size() - 1; k >= 0 && end == -1; --k) {
			if (!isspace(subblock[i][k])) {
				end = k;
			}
		}

		if (start != -1 && end != -1) {
			subblock[i] = subblock[i].substr(start, end - start + 1);
		}
	}
}

inline bool isFullyEmpty(const std::string & sTest) {
	for (int i = 0; i < sTest.size(); ++i) {
		if (!isspace(sTest[i])) {
			return false;
		}
	}
	
	return true;
}

void fatal(const std::string & errMsg) {
	cout << "[FATAL] " << errMsg << "\n";
	cout << "[FATAL] Exiting. Press Enter to continue.\n";
	cin.get();
	exit(1);
}