#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <windows.h>
using std::cin;
using std::cout;

#include "SubFilter.h"

int main() {
	std::string subFilename;
	bool filtered = false;
	int filesFiltered = 0;
	int processedFiles = 0;
	int totalFiles = 0;
	std::string sTemp;
	std::vector<std::string> blacklist;
	std::string blacklistFilename = "F:/Users/Mauri/Videos/WordBlacklist.txt";
	std::string sublistFilename = "F:/Users/Mauri/Videos/RecentlyCreatedSubFiles.txt";
	std::string logFilename = "F:/Users/Mauri/Videos/SubFilter.log";

	std::ofstream wLogfile(logFilename, std::ios::trunc);
	wLogfile.close();

	std::ifstream rBlacklistFile(blacklistFilename);
	if (!rBlacklistFile.good()) {
		cout << "File " << getBasename(blacklistFilename) << " can't be read from.\n";
		cout << "Press Enter to continue.\n";
		cin.get();
		exit(1);
	}

	std::ifstream rSublistFile(sublistFilename);
	if (!rSublistFile.good()) {
		cout << "File '" << getBasename(sublistFilename) << "' can't be read from.\n";
		cout << "Press Enter to continue.\n";
		cin.get();
		exit(1);
	}

	// read from blacklist txt
	while (std::getline(rBlacklistFile, sTemp)) {
		if (!sTemp.empty()) {
			blacklist.push_back(sTemp);
		}
	}

	// read number of files (each line contains path to file)
	while (std::getline(rSublistFile, subFilename)) {
		++totalFiles;
	}

	rSublistFile.clear();
	rSublistFile.seekg(0, std::ios::beg);

	// read from sub files list txt and send to processing
	while (std::getline(rSublistFile, subFilename)) {
		sTemp = getEpisodeStr(subFilename);
		if (!sTemp.empty()) {
			blacklist.push_back(sTemp);
		}
		filesFiltered += filterSubfile(subFilename, blacklist, logFilename);
		++processedFiles;
		cout << processedFiles << " of " << totalFiles << " files processed. \r";
	}

	cout << filesFiltered << " of " << processedFiles << " files were filtered.\n\nDone.\n";
	cout << "Press Enter to continue.\n";
	cin.get();
	return 0;
}