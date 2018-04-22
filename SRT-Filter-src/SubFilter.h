#ifndef SUBFILTER_H
#define SUBFILTER_H

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <fstream>
#include <regex>
#include <string>
#include <vector>
using std::cin;
using std::cout;

bool filterSubfile(const std::string &subFilename, const std::vector<std::string> & creditslist, const std::string & logFilename, std::ofstream & wLogfile);
std::string getIniValue(const std::string & iniKey);
void isSubfileDirty(std::vector<std::vector<std::string>> & toProceedBoolList, const std::vector<std::string> & creditslist, std::vector<std::string> subfileContents);
inline bool subblockHascredits(const std::vector <std::string> & creditslist, std::vector<std::string> subblock);
std::string getEpisodeStr(const std::string & subFilename);
bool isColorTagged(const std::vector<std::string> & subblock);
void removeFontTags(std::vector<std::string> & subblock);
void fixTags(std::vector<std::string> & subblock);
void removeEmptySubLines(std::vector <std::string> & subblock);
bool isTimeStamp(const std::string & sTest);
std::string getBasename(const std::string &filepath);
bool isFullyEmpty(const std::string & sTest);
void fatal(const std::string & errMsg);

#endif
