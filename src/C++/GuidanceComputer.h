//
// Created by Guillem Castro on 12/03/2017.
//

#include "Config.h"

#ifndef C_APPLICATION_H
#define C_APPLICATION_H


class GuidanceComputer {

public:

    GuidanceComputer(std::string configFilePath);

    void run();

private:

    Config config;

};


#endif //C_APPLICATION_H
