from abc import ABC, abstractmethod

class PC:
    def __init__(self, name):
        self.cpu = ""
        self.cpuCooler = ""
        self.motherboard = ""
        self.memory = ""
        self.gpu = ""
        self.psu = ""
        self.case = ""
        self.additionalFans = None

@abstractmethod
class Component(ABC): #An abstract class, defensive, prevents accidentally instantiating a Component object
    def __init__(self, name, price, powerConsumption, manufacturer):
        self.name = name
        self.manufacturer = manufacturer
        self.price = price
        self.powerConsumption = powerConsumption

class CPU(Component):
    def __init__(self, name, price, powerConsumption, manufacturer, chipset, compatibleChipsets, numberOfCores):
        super().__init__(name, price, powerConsumption, manufacturer)
        self.chipset = chipset
        self.compatibleChipsets = compatibleChipsets
        self.numberOfCores = numberOfCores

class Motherboard(Component):
    def __init__(self, name, price, powerConsumption, manufacturer, chipset, memoryCapacity):
        super().__init__(name, price, powerConsumption, manufacturer)
        self.chipset = chipset
        self.memoryCapacity = memoryCapacity

class GPU(Component):
    def __init__(self, name, price, powerConsumption, manufacturer, vram, architecture, numberOfCores, rayTracingCompatibility):
        super().__init__(name, price, powerConsumption, manufacturer)
        self.vram = vram
        self.architecture = architecture
        self.numberOfCores = numberOfCores
        self.rayTracingCompatibility = rayTracingCompatibility

class PowerSupply(Component):
    def __init__(self, name, price, powerConsumption, manufacturer, wattage, efficiencyRating):
        super().__init__(name, price, powerConsumption, manufacturer)
        self.wattage = wattage
        self.efficiencyRating = efficiencyRating

class RAM(Component):
    def __init__(self, name, price, powerConsumption, manufacturer, castLatency, frequency, capacity, dualChannelKitOrNo):
        super().__init__(name, price, powerConsumption, manufacturer)
        self.castLatency = castLatency
        self.frequency = frequency
        self.capacity = capacity
        self.dualChannelKitOrNo = dualChannelKitOrNo

class Storage(Component):
    def __init__(self, name, price, powerConsumption, manufacturer, capacity, typeOfStorage):
        super().__init__(name, price, powerConsumption, manufacturer)
        self.capacity = capacity
        self.typeOfStorage = typeOfStorage

class Case(Component):
    def __init__(self, name, price, powerConsumption, manufacturer, gpuClearance, powerSupplyTypesThatFit):
        super().__init__(name, price, powerConsumption, manufacturer)
        self.gpuClearance = gpuClearance
        self.powerSupplyTypesThatFit = powerSupplyTypesThatFit
        self.powerConsumption = 0

class CoolerCPU(Component):
    def __init__(self, name, price, powerConsumption, manufacturer, clearance):
        super().__init__(name, price, powerConsumption, manufacturer)
        self.clearance = clearance

