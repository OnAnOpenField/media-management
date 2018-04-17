#include "SubFilter.h"

// remove subtitle credits and strip font color tags
bool filterSubfile(const std::string &subFilename, const std::vector<std::string> &blacklist, const std::string & logFilename) {
	std::vector <std::string> subfileContents;
	std::vector <std::string> subblock;
	std::vector <std::string> subblock_old;
	std::string sTemp;
	int lineNum = 1, wLineNum = 1;

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

	//open log file for writing
	std::ofstream wLogfile(logFilename, std::ios::app);
	if (!wLogfile.good()) {
		std::cerr << "'" << getBasename(logFilename) << "' could not be opened for writing\n";
		return false;
	}

	bool subfileisSDH = isSDHBracketed(subfileContents);
	bool subfileIsDirty = isSubblockDirty(blacklist, subfileContents);
	bool subfileisColorTagged = isColorTagged(subfileContents);

	if (subfileisSDH) {
		std::string sCommand = "SubtitleEdit /convert \"" + subFilename + "\" SubRip /overwrite /fixcommonerrors /redocasing /removetextforhi > nul";
		system(sCommand.c_str());
		cout << "Removed SDH text from " << getBasename(subFilename) << "\n";
		wLogfile << "Removed SDH text from " << getBasename(subFilename) << "\n";
	}

	//check if subs are dirty or has color tags
	if (!subfileIsDirty && !subfileisColorTagged) {
		if (subfileisSDH) {
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

	//write to file
	for (int i = 0; i < subfileContents.size() - 2 && subfileContents.size() > 2; ++i) {
		if (isTimeStamp(subfileContents[i + 1])) {
			continue;
		}

		subblock.push_back(subfileContents[i]);
		if (isTimeStamp(subfileContents[i + 2]) || i + 3 == subfileContents.size()) {
			if (i + 3 == subfileContents.size()) {
				subblock.push_back(subfileContents[i + 1]);
				subblock.push_back(subfileContents[i + 2]);
			}

			if (isColorTagged(subblock)) {
				for (int i = 0; i < subblock.size(); ++i) {
					subblock_old.push_back(subblock[i]);
				}

				fixTags(subblock);
				cout << "    Line " << lineNum << " color tags removed:\n";
				wLogfile << "    Line " << lineNum << " color tags removed:\n";
				removeFontTags(subblock);

				for (int i = 1; i < subblock.size(); ++i) {
					cout << "    >> " << subblock_old[i] << " --> " << subblock[i] << "\n";
					wLogfile << "    >> " << subblock_old[i] << " --> " << subblock[i] << "\n";
				}

				cout << "\n";
				wLogfile << "\n";
				removeEmptySubLines(subblock);
				subblock_old.clear();

				if (subblock.size() == 1) {
					subblock.clear();
					continue;
				}
			}

			if (!isSubblockDirty(blacklist, subblock)) {
				wSubfile << wLineNum << "\n";
				++wLineNum;

				for (int i = 0; i < subblock.size(); ++i) {
					wSubfile << subblock[i] << "\n";
				}
				wSubfile << "\n";
			}
			else {
				cout << "    Line " << lineNum << " filtered:\n";
				wLogfile << "    Line " << lineNum << " filtered:\n";

				for (int i = 0; i < subblock.size(); ++i) {
					cout << "    >> " << subblock[i] << "\n";
					wLogfile << "    >> " << subblock[i] << "\n";
				}

				cout << "\n";
				wLogfile << "\n";
			}

			subblock.clear();
			++lineNum;
		}
	}

	return true;
}

bool isSubblockDirty(const std::vector <std::string> & blacklist, std::vector<std::string> subblock) {
	for (int i = 0; i<blacklist.size(); ++i) {
		for (int k = 0; k<subblock.size(); ++k) {
			std::regex e(blacklist[i], std::regex_constants::icase);
			if (regex_search(subblock[k], e)) {
				return true;
			}
		}
	}
	return false;
}

void removeEmptySubLines(std::vector <std::string>& subblock) {
	for (int i = 1; i < subblock.size(); ++i) {
		if (isFullyEmpty(subblock[i])) {
			subblock.erase(subblock.begin() + i);
		}
	}
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
		if (sTemp.find("<") != std::string::npos && sTemp.find("font") != std::string::npos && sTemp.find("font") != std::string::npos) {
			return true;
		}
	}

	return false;
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

void removeFontTags(std::vector <std::string> & subblock) {
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

bool isSDHBracketed(const std::vector<std::string>& subblock) {
	for (int i = 0; i < subblock.size(); ++i) {
		if (subblock[i].find('[') != std::string::npos) {
			return true;
		}
	}

	return false;
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
