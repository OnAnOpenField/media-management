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
	std::string creditslistFilename = getIniValue("SubCreditsListPath");
	std::string sublistFilename = getIniValue("RecentSubsPath");
	std::string logFilename = getIniValue("LogFilePath");

	std::ofstream wLogfile(logFilename, std::ios::trunc);
	if (!wLogfile.good()) {
		fatal("File \"" + logFilename + "\" could not be opened for reading.");
	}

	// open creditslist file for reading
	std::ifstream rCreditslistFile(creditslistFilename);
	if (!rCreditslistFile.good()) {
		fatal("File \"" + creditslistFilename + "\" could not be opened for reading.");
	}

	// Open SRT file list for reading
	std::ifstream rSublistFile(sublistFilename);
	if (!rSublistFile.good()) {
		fatal("File \"" + sublistFilename + "\" could not be opened for reading.");
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
		
		filesFiltered += filterSubfile(subFilename, creditslist, logFilename, wLogfile);
		++processedFiles;
		cout << processedFiles << " of " << totalFiles << " files processed. \r";
	}
	rSublistFile.close();
	
	cout << filesFiltered << " of " << totalFiles << " files were filtered.\n";
	wLogfile << filesFiltered << " of " << totalFiles << " files were filtered.";
	
	return 0;
}