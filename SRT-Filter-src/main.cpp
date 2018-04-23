#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using std::cin;
using std::cout;

#include "SubFilter.h"

int main() {
	bool filtered = false;
	int filesFiltered = 0;
	int processedFiles = 0;
	int totalFiles = 0;
	std::string sTemp;
	std::string subFilename;
	std::vector <std::string> creditslist;
	std::string SUBFILTER_LOG_PATH = getIniValue("LogFilePath");
	std::string CREDITS_LIST_PATH = getIniValue("SubCreditsListPath");
	std::string RECENT_SUBS_PATH = getIniValue("RecentSubsPath");

	std::ofstream wLogfile(SUBFILTER_LOG_PATH, std::ios::trunc);
	if (!wLogfile.good()) {
		fatal("File \"" + SUBFILTER_LOG_PATH + "\" could not be opened for reading.");
	}

	// open creditslist file for reading
	std::ifstream rCreditslistFile(CREDITS_LIST_PATH);
	if (!rCreditslistFile.good()) {
		fatal("File \"" + CREDITS_LIST_PATH + "\" could not be opened for reading.");
	}

	// Open SRT file list for reading
	std::ifstream rSublistFile(RECENT_SUBS_PATH);
	if (!rSublistFile.good()) {
		fatal("File \"" + RECENT_SUBS_PATH + "\" could not be opened for reading.");
	}

	// read from creditslist txt
	while (std::getline(rCreditslistFile, sTemp)) {
		if (!sTemp.empty()) {
			creditslist.push_back(sTemp);
		}
	}
	rCreditslistFile.close();

	// read number of files (each line contains path to file)
	while (std::getline(rSublistFile, sTemp)) {
		++totalFiles;
	}
	rSublistFile.clear();
	rSublistFile.seekg(0, std::ios::beg);

	// read from sub files list txt and send to processing
	while (std::getline(rSublistFile, subFilename)) {
		sTemp = getEpisodeStr(subFilename);
		if (!sTemp.empty()) {
			creditslist.push_back(sTemp);
		}
		
		filesFiltered += filterSubfile(subFilename, creditslist, wLogfile);
		++processedFiles;
		cout << processedFiles << " of " << totalFiles << " files processed. \r";
	}
	rSublistFile.close();
	
	cout << filesFiltered << " of " << totalFiles << " files were filtered.\n";
	wLogfile << filesFiltered << " of " << totalFiles << " files were filtered.";
	
	return 0;
}