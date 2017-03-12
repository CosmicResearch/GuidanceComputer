//
// Created by Guillem Castro on 12/03/2017.
//

#include "Config.h"

Config::Config() {

}

Config::Config(std::string configFilePath) {
    this->load(configFilePath);
}

bool Config::load(std::string configFilePath) {
    return false;
}