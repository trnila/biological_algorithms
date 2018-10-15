import utils


class Simulation:
    def __init__(self, space, algo, fn, options):
        self.step = 1
        self.algo = algo
        self.fn = fn
        self.options = options
        self.space = space

        cost_fn = utils.CountCallsProxy((lambda X: -fn(X)) if not options['min'] else fn)

        self.steps = []
        for step in algo.run(self.space, cost_fn, options):
            step.cost_fn_called = cost_fn.called_count

            def fix(unit):
                unit.cost *= -1
                return unit

            if not options['min']:
                step.points = [fix(p) for p in step.points]

            self.steps.append(step)

    @property
    def max_steps(self):
        return len(self.steps) - 1

    def step_by(self, n):
        self.step = max(1, min(self.max_steps, self.step + n))

    def step_forward(self):
        self.step_by(1)

    def step_back(self):
        self.step_by(-1)

    def current_step(self):
        return self.steps[self.step]

    def get_points(self):
        return self.steps[0:self.step]