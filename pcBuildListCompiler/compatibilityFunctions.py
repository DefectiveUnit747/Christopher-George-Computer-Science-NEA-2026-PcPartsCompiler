def isCpuCompatibleWithMotherboard(cpu, motherboard):
    return cpu["socket"] == motherboard["socket"]

def isMotherboardCompatibleWithRam(motherboard, ram):
    return motherboard["memoryType"] == ram["ddrType"]

def isGpuCompatibleWithCase(gpu, case):
    return gpu["length"] <= case["gpuMaxLength"]

def isMotherboardCompatibleWithCase(motherboard, case):
    return motherboard["formFactor"] in case["formFactorSupport"]

def isPsuCompatibleWithGpu(psu, gpu):
    return psu["wattage"] >= gpu["tdp"]

def isPsuCompatibleWithCpu(psu, cpu):
    return psu["wattage"] >= cpu["tdp"]

def isPsuCompatibleWithMotherboard(psu, motherboard):
    return psu["wattage"] >= motherboard["tdp"]

def isRamCapacityCompatibleWithMotherboard(ram, motherboard):
    return ram["numberOfModules"] <= motherboard["memorySlots"]