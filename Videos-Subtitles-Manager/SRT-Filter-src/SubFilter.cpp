#include "SubFilter.h"

// remove subtitle credits and strip font color tags
bool filterSubfile(const std::string &subFilename, const std::vector<std::string> & creditslist, const std::string & logFilename, std::ofstream & wLogfile) {
	std::vector<std::vector<std::string>> toProceedBoolList;
	std::vector<std::string> subfileContents;
	std::vector<std::vector<std::string>> newSubfileContents;
	std::vector<std::string> subblock;
	std::vector<std::string> subblock_old;
	std::string sTemp;
	int lineNum = 1;
	int wLineNum = 1;

	//open sub file for reading
	std::ifstream rSubfile(subFilename);
	if (!rSubfile.good()) {
		std::cerr << "'" << getBasename(subFilename) << "' could not be opened for reading\n";
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

	toProceedBoolList.push_back({ "hasCredits", "0" });
	toProceedBoolList.push_back({ "hasColorTags", "0" });
	toProceedBoolList.push_back({ "hasSDH", "0" });
	isSubfileDirty(toProceedBoolList, creditslist, subfileContents);

	bool subfileHasCredits = (toProceedBoolList[0][1] == "1");
	bool subfileisColorTagged = (toProceedBoolList[1][1] == "1");
	bool subfileisSDH = (toProceedBoolList[2][1] == "1");
	

	//check if subs are dirty or has color tags
	if (!subfileHasCredits && !subfileisColorTagged) {
		if (subfileisSDH) {
			std::string sCommand = "SubtitleEdit /convert \"" + subFilename + "\" SubRip /overwrite /fixcommonerrors /redocasing /removetextforhi > nul";
			system(sCommand.c_str());
			cout << "Removed SDH text from " << getBasename(subFilename) << "\n";
			wLogfile << "Removed SDH text from " << getBasename(subFilename) << "\n";
			return true;
		}
		return false;
	}

	//open sub file for writing
	std::ofstream wSubfile(subFilename, std::ios::trunc);
	if (!wSubfile.good()) {
		std::cerr << "'" << getBasename(subFilename) << "' could not be opened for writing\n";
		return false;
	}

	cout << "Filtering '" << getBasename(subFilename) << "'\n\n";
	wLogfile << "Filtering '" << getBasename(subFilename) << "'\n\n";

	for (int i = 0; i < subfileContents.size() - 1; ++i) {
		// if is sub line number
		if (!isTimeStamp(subfileContents[i + 1])) {
			subblock.push_back(subfileContents[i]);
		}

		// if sub block has ended
		if (!subblock.empty() && isTimeStamp(subfileContents[i + 1]) || i + 2 >= subfileContents.size()) {
			if (i + 2 >= subfileContents.size()) {
				subblock.push_back(subfileContents[i + 1]);
			}

			// if sub block contains credits
			if (subfileHasCredits && subblockHascredits(creditslist, subblock)) {
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

	// write clean subs back to subtitle file
	for (int i = 0; i < newSubfileContents.size(); ++i) {
		wSubfile << wLineNum << "\n";
		for (int k = 0; k < newSubfileContents[i].size(); ++k) {
			wSubfile << newSubfileContents[i][k] << "\n";
		}
		wSubfile << "\n";
		++wLineNum;
	}
	

	return true;
}

std::string getIniValue(const std::string & iniParam) {
	std::ifstream rIniFile("config.ini");
	if (!rIniFile.good()) {
		cout << "'config.ini' not found. Press Enter to continue.\n";
		cin.get();
		exit(1);
	}

	std::string sTemp;

	while (std::getline(rIniFile, sTemp)) {
		if (sTemp.find(iniParam) == 0) {
			for (int i = iniParam.size(); i < sTemp.size(); ++i) {
				if (!isspace(sTemp[i]) && sTemp[i] != '=') {
					return sTemp.substr(i, sTemp.size() - 1);
				}
			}
		}
	}

	cout << iniParam << " not found in config.ini\n"
		<< "Exiting. Press Enter to continue.\n";
	cin.get();
	exit(1);
}

void isSubfileDirty(std::vector<std::vector<std::string>> & toProceedBoolList, const std::vector<std::string> & creditslist, std::vector<std::string> subfileContents) {
	for (int i = 0; i<creditslist.size(); ++i) {
		for (int k = 0; k<subfileContents.size(); ++k) {
			std::regex e(creditslist[i], std::regex_constants::icase);
			if (regex_search(subfileContents[k], e)) {
				toProceedBoolList[0][1] = "1";
				goto fi;
			}
		}
	}

fi:

	std::string sTemp;

	for (int i = 0; i < subfileContents.size(); ++i) {
		sTemp = subfileContents[i];
		std::transform(sTemp.begin(), sTemp.end(), sTemp.begin(), ::tolower);
		if (sTemp.find('<') != std::string::npos && sTemp.find("font") != std::string::npos && sTemp.find('=') != std::string::npos) {
			toProceedBoolList[1][1] = "1";
			break;
		}
	}

	for (int i = 0; i < subfileContents.size(); ++i) {
		if (subfileContents[i].find('[') != std::string::npos) {
			toProceedBoolList[2][1] = "1";
			break;
		}
	}
}

inline bool subblockHascredits(const std::vector <std::string> & creditslist, std::vector<std::string> subblock) {
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

std::string getEpisodeStr(const std::string & subFilename) {
	std::smatch sm;
	std::regex e("s[0-9][0-9]e[0-9][0-9]", std::regex_constants::icase);

	std::regex_search(subFilename, sm, e);

	return sm[0];
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

void removeEmptySubLines(std::vector <std::string> & subblock) {
	for (int i = 0; i < subblock.size(); ++i) {
		if (isFullyEmpty(subblock[i])) {
			subblock.erase(subblock.begin() + i);
		}
	}
}

bool isTimeStamp(const std::string & sTest) {
	std::regex e("[0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9]");
	return regex_search(sTest, e);
}

std::string getBasename(const std::string & filepath) {
	for (int i = filepath.size() - 1; i >= 0; --i) {
		if (filepath[i] == '/' || filepath[i] == '\\') {
			return filepath.substr(i + 1, filepath.size() - i);
		}
	}
	return filepath;
}

bool isFullyEmpty(const std::string & sTest) {
	for (int i = 0; i < sTest.size(); ++i) {
		if (!isspace(sTest[i])) {
			return false;
		}
	}
	return true;
}
