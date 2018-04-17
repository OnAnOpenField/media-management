#ifndef SUBFILTER_H
#define SUBFILTER_H

#include <algorithm>
#include <iostream>
#include <fstream>
#include <regex>
#include <sstream>
#include <string>
#include <vector>
using std::cin;
using std::cout;

bool filterSubfile(const std::string &subFilename, const std::vector<std::string> &blacklist, const std::string & logFilename);
bool isSubblockDirty(const std::vector <std::string> & blacklist, std::vector<std::string> subblock);
void removeEmptySubLines(std::vector <std::string> & subblock);
std::string getEpisodeStr(const std::string & subFilename);
bool isColorTagged(const std::vector<std::string> & subblock);
void fixTags(std::vector<std::string> & subblock);
void removeFontTags(std::vector<std::string> & subblock);
bool isSDHBracketed(const std::vector<std::string> & subblock);
bool isTimeStamp(const std::string & sTest);
void strip(std::string &filepath);
std::string getBasename(const std::string &filepath);
bool isFullyEmpty(const std::string & sTest);

#endif
