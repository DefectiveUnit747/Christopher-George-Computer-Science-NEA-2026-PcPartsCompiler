def isCpuCompatibleWithMotherboard(cpu, motherboard):
    return cpu["socketId"] == motherboard["socketId"]

def isMotherboardCompatibleWithRam(motherboard, ram):
    return motherboard["memoryType"] == ram["ddrType"]

def isGpuCompatibleWithCase(gpu, case):
    return gpu["lengthMm"] <= case["gpuMaxLength"]

def isMotherboardCompatibleWithCase(motherboard, case):
    return motherboard["formFactor"] in case["formFactorSupport"]

def isPsuCompatibleWithGpu(psu, gpu):
    return psu["wattage"] >= gpu["tdpWatts"]

def isPsuCompatibleWithCpu(psu, cpu):
    return psu["wattage"] >= cpu["tdpWatts"]

def isPsuCompatibleWithMotherboard(psu, motherboard):
    return psu["wattage"] >= motherboard["tdpWatts"]

def isRamCapacityCompatibleWithMotherboard(ram, motherboard):
    return ram["numberOfModules"] <= motherboard["memorySlots"]
