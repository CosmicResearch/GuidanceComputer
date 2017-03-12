//
// Created by Guillem Castro on 12/03/2017.
//

#ifndef C_CONFIG_H
#define C_CONFIG_H

#include <string>


class Config {

public:

    Config();

    Config(std::string configFilePath);

    bool load(std::string configFilePath);

private:

    int powerLedPin;
    int okLedPin;

};


#endif //C_CONFIG_H
