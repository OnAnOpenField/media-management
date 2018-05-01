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

bool filterSubfile(const std::string &subFilename, const std::vector <std::string> & creditslist, std::ofstream & wLogfile);
std::string getIniValue(const std::string & iniKey);
std::string getEpisodeStr(const std::string & subFilename);
void isSubfileDirty(std::vector <std::vector <std::string>> & toProceedBoolList, const std::vector <std::string> & creditslist, std::vector <std::string> subfileContents);
bool hasTextForHI(const std::vector <std::string> subblock);
void removeTextForHI(std::vector <std::string> & subblock);
bool isColorTagged(const std::vector <std::string> & subblock);
void removeFontTags(std::vector <std::string> & subblock);
void fixTags(std::vector <std::string> & subblock);
inline bool hasCredits(const std::vector <std::string> & creditslist, const std::vector <std::string> subblock);
void removeEmptySubLines(std::vector <std::string> & subblock);
inline bool isTimeStamp(const std::string & sTest);
void trim(std::vector <std::string> & subblock);
inline bool isFullyEmpty(const std::string & sTest);
void fatal(const std::string & errMsg);

#endif
