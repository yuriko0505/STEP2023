from datetime import datetime
import enum
import functools as ft
import itertools as it
import math
import random
import matplotlib.pyplot as plt
import numpy as np


@enum.unique
class Breed(enum.Enum):
    ScrambleMutation = enum.auto()
    TranslocationMutation = enum.auto()
    SwapAdjacentPoints = enum.auto()
    SwapMutation = enum.auto()
    InversionMutation = enum.auto()
    CyclicCrossover = enum.auto()
    PartialCrossover = enum.auto()
    OrderCrossover = enum.auto()
    # OrderBasedCrossover = enum.auto()
    PositionBasedCrossover = enum.auto()
    # PartiallyMappedCrossOver = enum.auto()
    # SubtourExchangeCrossOver = enum.auto()
    # EdgeRecombinationCrossOver = enum.auto()
    # EdgeAssemblyCrossOver = enum.auto()
    SinglePtCrossover = enum.auto()
    TwoPtsCrossover = enum.auto()
    MultiPtsCrossover = enum.auto()
    UniformCrossover = enum.auto()
    SubstitutionMutation = enum.auto()


## Coords of customers, all of which each salesman must travel.
## Generic property of the Salesmans
class Species:
    MIN_FITNESS = -100000
    fig_projection = None  # '3d' to plot a salesman's path on 3D

    def __init__(self, points:np.ndarray=None, N:int=10, seed=None, *args, **kwargs):
        if points is None:
            np.random.seed(seed)
            points = np.random.randn(N, 2)
            np.random.seed(None)
        self.points = points
        self.N = self.points.shape[0]
        self.indeces = np.arange(self.N, dtype=int)
        self._prepare(*args, **kwargs)

    def _prepare(self, *args, **kwargs):
        self._to_origin = np.sqrt(np.sum(self.points ** 2, axis=1))
        self._distance_map = np.zeros((self.N, self.N), dtype=np.float)
        for idx in range(self.N):
            xy_dist = np.sqrt(np.sum((self.points[idx]-self.points[:])**2, axis=1))
            self._distance_map[idx] = xy_dist

    def measure(self, path, *args, **kwargs):
        length = self._distance_map[path[:-1], path[1:]].sum()
        length += self._to_origin[path[0]]
        length += self._to_origin[path[-1]]
        return length

    def bonus(self, path, *args, **kwargs):
        bonus = 0.0
        return bonus

    def penalty(self, path, *args, **kwargs):
        penalty = 0.0
        return penalty

    def evaluate(self, path, *args, **kwargs):
        length = self.measure(path=path, *args, **kwargs)
        bonus = self.bonus(path=path, *args, **kwargs)
        penalty = self.penalty(path=path, *args, **kwargs)
        fitness = - length + bonus - penalty
        return fitness, length

    def plot_a_path(self, ax, path, plot_kwargs={}, *args, **kwargs):
        coords = self.points[path]
        ax.plot(coords[:,0], coords[:,1], **plot_kwargs)
        ax.plot((coords[-1,0], 0, coords[0,0]), (coords[-1,1], 0, coords[0,1]), **plot_kwargs)
        ax.scatter([coords[0,0]], [coords[0,1]])
        abs_max_val = np.max(np.abs(self.points)) * 1.1
        lim = (-abs_max_val, abs_max_val)
        ax.set_xlim(lim)
        ax.set_ylim(lim)


## Indivisual Salesman
class Salesman:
    _breeders = None  # initialized by Salesman.breed()

    def __init__(self, species:Species, path=None, picked_indeces=None, *args, **kwargs):
        self.species = species
        self._fitness = None
        self._length = None
        self.__indeces = None
        if path is not None:
            self.path = path if isinstance(path, np.ndarray) else np.array(path)
            self._picked_indeces = None
        elif picked_indeces is not None:  # encode picked_indeces to path.
            self._picked_indeces = picked_indeces if isinstance(picked_indeces, np.ndarray) else np.array(picked_indeces)
            indeces = np.arange(self.species.N, dtype=int)
            self.path = np.zeros(self.species.N, dtype=int)
            for idx, gene in enumerate(picked_indeces):
                self.path[idx] = indeces[gene]
                indeces[gene:-1] = indeces[gene+1:]
        else:  # generate new.
            self.path = np.random.permutation(self.species.N)
            self._picked_indeces = None
        self._hash = tuple(self.path).__hash__()

    def __hash__(self):
        return self._hash

    def __eq__(self, theother):
        return self.__hash__() == theother.__hash__()

    def __repr__(self):
        return f'- fitness: {self.fitness:.3f}\n- length: {self.length:.3f}\n- path: {self.path}'

    @property
    def picked_indeces(self):
        if self._picked_indeces is None:  # encode path to picked_indeces.
            bits = np.ones(self.species.N, dtype=np.int)
            self._picked_indeces = np.zeros(self.species.N, dtype=int)
            for idx, p in enumerate(self.path):
                self._picked_indeces[idx] = np.sum(bits[:p], initial=0)
                bits[p] = 0
        return self._picked_indeces

    @property
    def fitness(self):
        self._evaluate()
        return self._fitness

    @property
    def length(self):
        self._evaluate()
        return self._length

    def _evaluate(self):
        if self._fitness is None:
            self._fitness, self._length = self.species.evaluate(self.path)

    @property
    def _indeces(self):
        if self.__indeces is None:
            self.__indeces = np.zeros(self.species.N, dtype=int)
            self.__indeces[self.path] = self.species.indeces
        return self.__indeces

    def plot(self, ax, show_title:bool=True, plot_kwargs={}, *args, **kwargs):
        self.species.plot_a_path(ax=ax, path=self.path, plot_kwargs=plot_kwargs, *args, **kwargs)
        ax.legend()
        if show_title:
            title = plot_kwargs.get('label', '') + f': fit {self.fitness:.3f} / len {self.length:.3f}'
            ax.set_title(title)

    @staticmethod
    def sample_betters(salesmans, k:int, nelites:int=0, *args, **kwargs):
        salesmans = salesmans if isinstance(salesmans, tuple) or isinstance(salesmans, list) else tuple(salesmans)
        fits = np.array([s.fitness for s in salesmans])
        # select some part of k by roulette.
        fit_ave = fits.mean()
        fit_std = fits.std()
        weights = 1.0 / (1.0 + np.exp((fit_ave - fits) / fit_std))
        k1 = k if nelites == 0 else random.randrange(k - nelites)
        yield from random.choices(salesmans, weights=weights, k=k1)
        # select elites.
        if nelites > 0:
            fit_elite = np.sort(fits)[-nelites]
            yield from (s for s in salesmans if s.fitness >= fit_elite)
            # select lest of k by roulette.
            k2 = k - k1 - nelites
            yield from random.choices(salesmans, weights=weights, k=k2)

    @staticmethod
    def scramble_mutation(mother:'Salesman', father:'Salesman', *args, **kwargs):
        idx0, idx1 = sorted(random.sample(range(mother.species.N-1), k=2))  # at least 3 points may be shuffled.
        child1 = mother._scramble_mutation(idx0, idx1)
        child2 = father._scramble_mutation(idx0, idx1)
        return child1, child2

    def _scramble_mutation(self, idx0:int, idx1:int, *args, **kwargs):
        child_path = self.path.copy()
        np.random.shuffle(child_path[idx0:idx1+2])
        child = Salesman(species=self.species, path=child_path)
        return child

    @staticmethod
    def translocation_mutation(mother:'Salesman', father:'Salesman', *args, **kwargs):
        idx0, idx1, idx2 = sorted(random.sample(range(mother.species.N+1), k=3))
        child1 = mother._translocation_mutation(idx0, idx1, idx2)
        child2 = father._translocation_mutation(idx0, idx1, idx2)
        return child1, child2

    def _translocation_mutation(self, idx0:int, idx1:int, idx2:int, *args, **kwargs):
        child_path = np.concatenate((self.path[:idx0], self.path[idx1:idx2], self.path[idx0:idx1], self.path[idx2:]))
        child = Salesman(species=self.species, path=child_path)
        return child

    @staticmethod
    def swap_adjacent_points(mother:'Salesman', father:'Salesman', *args, **kwargs):
        indeces = np.array(random.sample(range((mother.species.N-1)//2), k=mother.species.N//10), dtype=int) * 2
        child1 = mother._swap_adjacent_points(indeces)
        child2 = father._swap_adjacent_points(indeces)
        return child1, child2

    def _swap_adjacent_points(self, indeces, *args, **kwargs):
        child_path = self.path.copy()
        child_path[indeces], child_path[indeces+1] = child_path[indeces+1], child_path[indeces]
        child = Salesman(species=self.species, path=child_path)
        return child

    @staticmethod
    def swap_mutation(mother:'Salesman', father:'Salesman', *args, **kwargs):
        idx0, idx1, idx2, idx3 = sorted(random.sample(range(mother.species.N), k=4))
        child1 = mother._swap_mutation(idx0, idx1, idx2, idx3)
        child2 = father._swap_mutation(idx0, idx1, idx2, idx3)
        return child1, child2

    def _swap_mutation(self, idx0:int, idx1:int, idx2:int, idx3:int, *args, **kwargs):
        child_path = np.concatenate((self.path[:idx0], self.path[idx2:idx3], self.path[idx1:idx2], self.path[idx0:idx1], self.path[idx3:]))
        child = Salesman(species=self.species, path=child_path)
        return child

    @staticmethod
    def inversion_mutation(mother:'Salesman', father:'Salesman', *args, **kwargs):
        idx0, idx1 = sorted(random.sample(range(mother.species.N-1), k=2))  # at least 3 points may be reversed.
        child1 = mother._inversion_mutation(idx0, idx1)
        child2 = father._inversion_mutation(idx0, idx1)
        return child1, child2

    def _inversion_mutation(self, idx0:int, idx1:int, *args, **kwargs):
        child_path = self.path.copy()
        child_path[idx0:idx1+2] = np.flip(self.path[idx0:idx1+2])
        child = Salesman(species=self.species, path=child_path)
        return child

    @staticmethod
    def cyclic_crossover(mother:'Salesman', father:'Salesman', *args, **kwargs):
        child1_path = mother.path.copy()
        child2_path = father.path.copy()
        idx = random.randrange(mother.species.N)
        val_1st = mother.path[idx]
        val_next = -1
        while val_next != val_1st:
            val_next = father.path[idx]
            child1_path[idx] = val_next
            child2_path[idx] = mother.path[idx]
            idx = mother._indeces[val_next]
        child1 = Salesman(species=mother.species, path=child1_path)
        child2 = Salesman(species=mother.species, path=child2_path)
        return child1, child2

    @staticmethod
    def partial_crossover(mother:'Salesman', father:'Salesman', *args, **kwargs):
        child1_path = mother.path.copy()
        child2_path = father.path.copy()
        child1_indeces = np.zeros(mother.species.N, dtype=int)
        child2_indeces = np.zeros(father.species.N, dtype=int)
        idx0, idx1 = sorted(random.sample(range(mother.species.N+1), k=2))  # at least 3 points may be reversed.
        for idx in range(idx0, idx1):
            child1_indeces[child1_path] = mother.species.indeces
            child2_indeces[child2_path] = father.species.indeces
            pt1 = child1_path[idx]
            pt2 = child2_path[idx]
            child1_path[idx] = pt2
            child2_path[idx] = pt1
            child1_path[child1_indeces[pt2]] = pt1
            child2_path[child2_indeces[pt1]] = pt2
        child1 = Salesman(species=mother.species, path=child1_path)
        child2 = Salesman(species=mother.species, path=child2_path)
        return child1, child2

    @staticmethod
    def order_crossover(mother:'Salesman', father:'Salesman', *args, **kwargs):
        idx = random.randrange(mother.species.N)
        child1 = mother._order_crossover(father, idx)
        child2 = father._order_crossover(mother, idx)
        return child1, child2

    def _order_crossover(self, other:'Salesman', idx, *args, **kwargs):
        head = self.path[:idx]
        tail = np.delete(other.path, other._indeces[head])
        child_path = np.concatenate((head, tail))
        child = Salesman(species=self.species, path=child_path)
        return child

    @staticmethod
    def position_based_crossover(mother:'Salesman', father:'Salesman', *args, **kwargs):
        flags = random.choices((0,1), k=mother.species.N)
        child1 = mother._position_based_crossover(father, flags)
        child2 = father._position_based_crossover(mother, flags)
        return child1, child2

    def _position_based_crossover(self, other:'Salesman', flags, *args, **kwargs):
        child_path = self.path.copy()
        swap_pts = self.path[flags == 1]
        child_path[flags == 0] = np.delete(other.path, other._indeces[swap_pts])
        child = Salesman(species=self.species, path=child_path)
        return child

    @staticmethod
    def single_pt_crossover(mother:'Salesman', father:'Salesman', *args, **kwargs):
        return Salesman._n_pts_crossover(mother, father, 1)

    @staticmethod
    def two_pts_crossover(mother:'Salesman', father:'Salesman', *args, **kwargs):
        return Salesman._n_pts_crossover(mother, father, 2)

    @staticmethod
    def multi_pts_crossover(mother:'Salesman', father:'Salesman', *args, **kwargs):
        return Salesman._n_pts_crossover(mother, father, mother.species.N // 4)

    @staticmethod
    def _n_pts_crossover(mother:'Salesman', father:'Salesman', k:int, *args, **kwargs):
        indeces = [None] + sorted(random.sample(range(mother.species.N), k=k)) + [None]
        child1_picked_indeces, child2_picked_indeces, *_ = ft.reduce(
                lambda gs, ii: (gs[0] + gs[2][ii[0]:ii[1]], gs[1] + gs[3][ii[0]:ii[1]], gs[3], gs[2]),
                zip(indeces[:-1], indeces[1:]),
                ([], [], list(mother.picked_indeces), list(father.picked_indeces)))
        child1 = Salesman(species=mother.species, picked_indeces=child1_picked_indeces)
        child2 = Salesman(species=mother.species, picked_indeces=child2_picked_indeces)
        return child1, child2

    @staticmethod
    def uniform_crossover(mother:'Salesman', father:'Salesman', *args, **kwargs):
        indeces = mother.species.indeces[random.choices((0,1), k=mother.species.N) == 1]
        child1 = mother._uniform_crossover(indeces)
        child2 = father._uniform_crossover(indeces)
        return child1, child2

    def _uniform_crossover(self, indeces, *args, **kwargs):
        child_picked_indeces = self.picked_indeces.copy()
        child_picked_indeces[indeces] = self.picked_indeces[indeces]
        child = Salesman(species=self.species, picked_indeces=child_picked_indeces)
        return child

    @staticmethod
    def substitution_mutation(mother:'Salesman', father:'Salesman', *args, **kwargs):
        child1 = mother._substitution_mutation()
        child2 = father._substitution_mutation()
        return child1, child2

    def _substitution_mutation(self, *args, **kwargs):
        N = self.species.N
        indeces = np.array([random.randint((idx-N)*N, N-idx-1) for idx in range(N)])
        child_picked_indeces = self.picked_indeces.copy()
        child_picked_indeces[indeces >= 0] = indeces[indeces >= 0]
        child = Salesman(species=self.species, picked_indeces=child_picked_indeces)
        return child

    @classmethod
    def breed(cls, breed:Breed, mother:'Salesman', father:'Salesman', *args, **kwargs):
        if cls._breeders is None:
            cls._breeders = {
                Breed.ScrambleMutation: Salesman.scramble_mutation,
                Breed.TranslocationMutation: Salesman.translocation_mutation,
                Breed.SwapAdjacentPoints: Salesman.swap_adjacent_points,
                Breed.SwapMutation: Salesman.swap_mutation,
                Breed.InversionMutation: Salesman.inversion_mutation,
                Breed.CyclicCrossover: Salesman.cyclic_crossover,
                Breed.PartialCrossover: Salesman.partial_crossover,
                Breed.OrderCrossover: Salesman.order_crossover,
                # Breed.OrderBasedCrossover: Salesman.order_based_crossover,
                Breed.PositionBasedCrossover: Salesman.position_based_crossover,
                Breed.SinglePtCrossover: Salesman.single_pt_crossover,
                Breed.TwoPtsCrossover: Salesman.two_pts_crossover,
                Breed.MultiPtsCrossover: Salesman.multi_pts_crossover,
                Breed.UniformCrossover: Salesman.uniform_crossover,
                Breed.SubstitutionMutation: Salesman.substitution_mutation,
            }
        breeder = cls._breeders.get(breed, lambda *_: None)
        return breeder(mother, father, *args, **kwargs)


## Group of Salesmans
class Generation:
    def __init__(self, species:Species, salesmans, *args, **kwargs):
        self.species = species
        self.salesmans = salesmans if isinstance(salesmans, tuple) else tuple(salesmans)
        self.leader = max(self.salesmans, key=lambda s: s.fitness)
        self.population = len(self.salesmans)

    @staticmethod
    def generate_0th(species:Species, population:int=1000, *args, **kwargs):
        children = set(Salesman(species=species) for _ in range(population - 1))
        children.add(Salesman(species=species, path=np.arange(species.N)))  # add the original path (0, 1, 2, ..., N-1)
        generation = Generation(species=species, salesmans=children)
        return generation


## Model of Genetic Algorithm for Traveling Salesman Problem.
class Model:
    def __init__(self, species:Species, max_population:int=None, *args, **kwargs):
        self.species = species
        self.max_population = int(species.N * math.log2(species.N)**2) if max_population is None else int(max_population)
        self.nelites = self.max_population // 10
        self.generation = Generation.generate_0th(species, self.max_population)
        self.breeded_population = 0
        self.leader_changed_epoch = 0
        self.stopped_epoch = 0
        self.breed_rates = {
            Breed.ScrambleMutation: 0.6,
            Breed.TranslocationMutation: 0.6,
            Breed.SwapAdjacentPoints: 0.6,
            Breed.SwapMutation: 0.6,
            Breed.InversionMutation: 0.6,
            Breed.CyclicCrossover: 0.6,
            Breed.PartialCrossover: 0.6,
            Breed.OrderCrossover: 0.6,
            # Breed.OrderBasedCrossover: 0.6,
            Breed.PositionBasedCrossover: 0.6,
            Breed.SinglePtCrossover: 0.6,
            Breed.TwoPtsCrossover: 0.6,
            Breed.MultiPtsCrossover: 0.6,
            Breed.UniformCrossover: 0.6,
            Breed.SubstitutionMutation: 0.6,
        }

    def fit(self, nepochs:int=None, loggers=(), *args, **kwargs):
        nepochs = int(self.species.N * math.log(self.species.N)**2) if nepochs is None else int(nepochs)
        epoch_to_stop = nepochs
        last_best_fitness = -1000000
        any(p.log_begin(self) for p in loggers)
        for epoch in range(nepochs):
            evoluated = self._evoluate(epoch)
            self.generation = Generation(species=self.species, salesmans=evoluated)
            if self.generation.leader.fitness > last_best_fitness:
                last_best_fitness = self.generation.leader.fitness
                self.leader_changed_epoch = epoch + 1
                epoch_to_stop = epoch + self.species.N
            any(p.log(self, epoch+1) for p in loggers)
            if epoch > epoch_to_stop:
                self.stopped_epoch = epoch + 1
                break
        any(p.log_end(self) for p in loggers)

    def _evoluate(self, epoch, *args, **kwargs):
        children = set(self.generation.salesmans)
        nparents = self.max_population - epoch * self.species.N // 10
        mothers = Salesman.sample_betters(self.generation.salesmans, nparents, self.nelites)
        fathers = Salesman.sample_betters(self.generation.salesmans, nparents, self.nelites)
        for _ in (children.update(Salesman.breed(breed, mother, father))
                for mother, father in zip(mothers, fathers) if mother != father
                for breed, rate in self.breed_rates.items() if random.random() < rate):
            pass
        self.breeded_population = len(children)
        betters = set(Salesman.sample_betters(children, self.max_population, self.nelites))
        return betters


## Loggers for Model.fit()
class Logger:
    COLORS=('red','green','blue','magenta','cyan')
    STYLES=('-','--','-.')
    _is_subplot = True
    _nlogs = 1

    def __init__(self, *args, **kwargs):
        pass

    def log_begin(self, model:Model, *args, **kwargs):
        self._logs = [[] for _ in range(self._nlogs)]
        self.log(model=model, epoch=0)

    def log_end(self, model:Model, *args, **kwargs):
        self._stopped_epoch = model.stopped_epoch

    def log(self, model:Model, epoch:int, *args, **kwargs):
        pass

    def plot(self, ax=None, epochs=None, *args, **kwargs):
        if epochs is None:
            nepochs = self._stopped_epoch
            epochs = (0, nepochs // 4, nepochs // 2, nepochs) if nepochs > 3 else (0, nepochs)
        self._plot(ax=ax, epochs=epochs, *args, **kwargs)

    def _plot(self, ax=None, epochs=None, *args, **kwargs):
        pass

    def _plot_epoch_lines(self, ax, epochs, y_lim, *args, **kwargs):
        ax.set_ylim(y_lim)
        for epoch in epochs:
            ax.plot((epoch, epoch), y_lim, color='gray', linestyle=':')

    def _offset_lim(self, y_min, y_max, *args, **kwargs):
        offset = (y_max - y_min) / 20
        return y_min - offset, y_max + offset

    @staticmethod
    def plot_all(loggers, epochs=None, *args, **kwargs):
        any(p.plot(ax=None, epochs=epochs, *args, **kwargs) for p in loggers if not p._is_subplot)
        subloggers = [p for p in loggers if p._is_subplot]
        if len(subloggers) > 0:
            axes = get_subplots(nax=len(subloggers))
            any(p.plot(ax=axes.pop(0), epochs=epochs, *args, **kwargs) for p in subloggers)
            plt.show()


class Logger_trace(Logger):
    _is_subplot = False

    def __init__(self, level:int=1, *args, **kwargs):
        self._level = level
        self._trace = self._l3 if level == 3 else self._l2 if level == 2 else (lambda *_: None)

    def log_begin(self, model:Model, *args, **kwargs):
        self._st = datetime.now()
        if self._level == 1:
            print('start at', self._st.strftime('%Y/%m/%d %H:%M:%S'))
        elif self._level == 2:
            print('start at', self._st.strftime('%Y/%m/%d %H:%M:%S'), end='')
        super().log_begin(model=model, *args, **kwargs)

    def log_end(self, model:Model, *args, **kwargs):
        et = datetime.now()
        super().log_end(model=model, *args, **kwargs)
        if self._level > 0:
            print(f'\n- time: {str(et - self._st)[:-3]}')
            print(f'- epoch: {model.stopped_epoch}({model.leader_changed_epoch})')
            print(f'{model.generation.leader}')

    def log(self, model:Model, epoch:int, *args, **kwargs):
        self._trace(model, epoch)

    def _l2(self, model:Model, epoch:int, *args, **kwargs):
        dot = '+' if epoch % 10 == 0 else '.'
        print(dot, end='')
        if epoch % 100 == 0:
            ct = datetime.now()
            print(f' fitness: {model.generation.leader.fitness:.3f}({model.leader_changed_epoch}) {str(ct - self._st)[:-3]}')

    def _l3(self, model:Model, epoch:int, *args, **kwargs):
        if epoch % 10 == 0:
            print(f'{epoch}: {model.generation.leader}')


class Logger_leaders(Logger):
    _is_subplot = False

    def log_begin(self, model:Model, *args, **kwargs):
        super().log_begin(model=model, *args, **kwargs)
        self._original = Salesman(model.species, path=model.species.indeces)
        self._projection = model.species.fig_projection

    def log(self, model:Model, epoch:int, *args, **kwargs):
        self._logs[0].append(model.generation.leader)

    def _plot(self, ax=None, epochs=None, *args, **kwargs):
        nplots = len(epochs)
        axes = get_subplots(nax=nplots+1, projection=self._projection)
        self._original.plot(ax=axes.pop(0), plot_kwargs=dict(label=f'original'))
        for epoch in epochs:
            self._logs[0][epoch].plot(ax=axes.pop(0), plot_kwargs=dict(label=f'{epoch}th'))
        plt.show()


class Logger_fitness(Logger):
    _nlogs = 2

    def log(self, model:Model, epoch:int, *args, **kwargs):
        self._logs[0].append(model.generation.leader.fitness)
        self._logs[1].append(sum(s.fitness for s in model.generation.salesmans) / model.generation.population)

    def _plot(self, ax, epochs=None, *args, **kwargs):
        xs = np.arange(len(self._logs[0]))
        ax.plot(xs, self._logs[0], label='best in the history', color=(0,0,1))
        ax.plot(xs, self._logs[1], label='average of each generation', color=(0,0,1), linestyle='--')
        y_lim = self._offset_lim(min(self._logs[0]), max(self._logs[0]))
        self._plot_epoch_lines(ax, epochs, y_lim)
        ax.set_xlabel('generation')
        ax.set_ylabel('fitness')
        ax.set_title('fitness')
        ax.legend()


class Logger_population(Logger):
    _nlogs = 2

    def __init__(self, show_breeded:bool=False, *arggs, **kwargs):
        self._show_breeded = show_breeded

    def log_begin(self, model:Model, *args, **kwargs):
        super().log_begin(model=model, *args, **kwargs)
        self._max_population = model.max_population

    def log(self, model:Model, epoch:int, *args, **kwargs):
        self._logs[0].append(model.generation.population)
        self._logs[1].append(model.breeded_population)

    def _plot(self, ax=None, epochs=None, *args, **kwargs):
        xs = np.arange(len(self._logs[0]))
        ax.plot(xs, [v for v in self._logs[0]], label='population')
        if self._show_breeded:
            ax.plot(xs, [v for v in self._logs[1]], label='breeded')
            y_max = max(self._logs[1])
        else:
            y_max = max(self._logs[0])
        ax.plot((epochs[0], epochs[-1]), (self._max_population, self._max_population), color='gray', linestyle=':')
        y_lim = self._offset_lim(min(self._logs[0]), y_max)
        self._plot_epoch_lines(ax, epochs, y_lim)
        ax.set_xlabel('epoch')
        ax.set_ylabel('population')
        ax.set_title('population')
        ax.legend()


class Logger_last_fitness_histgram(Logger):
    def log_end(self, model:Model, *args, **kwargs):
        super().log_end(model=model, *args, **kwargs)
        self._logs[0] = [s.fitness for s in model.generation.salesmans]

    def _plot(self, ax=None, epochs=None, *args, **kwargs):
        ax.hist(self._logs[0], 20)
        ax.set_xlabel('fitness')
        ax.set_ylabel('count of salesmans')
        ax.set_title('fitnesses at last')


class Logger_breed_legend(Logger):
    def _plot(self, ax=None, epochs=None, *args, **kwargs):
        for breed, color, style in zip(Breed, it.cycle(self.COLORS), it.cycle(self.STYLES)):
            ax.plot((0, 1), (0, 0), label=f'{breed.value} {breed}', color=color, linestyle=style)
        ax.legend()
        ax.set_xlim((0.0, 1.0))
        ax.set_xticks(())
        ax.set_ylim((0.0, 1.0))
        ax.set_yticks(())
        ax.set_title('legend')


## support functions.
def get_subplots(nax=1, *args, **kwargs):
    rows = 1 if nax == 5 else (nax + 3) // 4
    cols = 5 if nax == 5 else 4 if nax > 4 else nax
    fig = plt.figure()
    fig.set_figwidth(20.0)
    fig.set_figheight(rows * (20 // cols))
    axes = [fig.add_subplot(rows, cols, ridx * cols + cidx + 1, *args, **kwargs) for ridx in range(rows) for cidx in range(cols)]
    return axes
