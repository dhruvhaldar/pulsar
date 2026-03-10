import numpy as np

class Component:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Mass(Component):
    def __init__(self, name, m):
        super().__init__(name, m)

class Spring(Component):
    def __init__(self, name, k):
        super().__init__(name, k)

class Damper(Component):
    def __init__(self, name, c):
        super().__init__(name, c)

class Resistor(Component):
    def __init__(self, name, r):
        super().__init__(name, r)

class Capacitor(Component):
    def __init__(self, name, c):
        super().__init__(name, c)

class Inductor(Component):
    def __init__(self, name, l):
        super().__init__(name, l)

class System:
    def __init__(self, domain="mechanical"):
        self.domain = domain
        self.components = []

    def add_component(self, component):
        self.components.append(component)

    def assemble(self):
        """
        Assemble the components into a state-space representation.
        \dot{x} = Ax + Bu
        y = Cx + Du
        Returns A, B, C, D matrices.
        """
        # A simple placeholder assembly for mass-spring-damper or RLC circuit
        # A real solver would parse graph connections. We'll support a simple series RLC or MSD
        if self.domain == "mechanical":
            m, k, c = 1.0, 1.0, 1.0
            for comp in self.components:
                if isinstance(comp, Mass): m = comp.value
                elif isinstance(comp, Spring): k = comp.value
                elif isinstance(comp, Damper): c = comp.value

            # x1 = position, x2 = velocity
            # dx1/dt = x2
            # dx2/dt = (-k/m)*x1 + (-c/m)*x2 + (1/m)*u
            A = np.array([[0, 1],
                          [-k/m, -c/m]])
            B = np.array([[0],
                          [1/m]])
            C = np.array([[1, 0]])
            D = np.array([[0]])
            return A, B, C, D

        elif self.domain == "electrical":
            # series RLC: x1 = voltage across C, x2 = current through L
            # u = voltage source
            # dx1/dt = 1/C * x2
            # dx2/dt = -1/(L*C)*x1 - R/L*x2 + 1/L*u (Wait, dIL/dt = 1/L*(u - R*IL - VC))
            # dVC/dt = 1/C * IL

            r, l_val, c_val = 1.0, 1.0, 1.0
            for comp in self.components:
                if isinstance(comp, Resistor): r = comp.value
                elif isinstance(comp, Inductor): l_val = comp.value
                elif isinstance(comp, Capacitor): c_val = comp.value

            A = np.array([[0, 1/c_val],
                          [-1/l_val, -r/l_val]])
            B = np.array([[0],
                          [1/l_val]])
            C = np.array([[1, 0]]) # Output voltage across C
            D = np.array([[0]])
            return A, B, C, D

        else:
            raise ValueError(f"Unknown domain {self.domain}")
