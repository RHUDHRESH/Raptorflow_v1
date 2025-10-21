"""
Quantum-Inspired Optimization Engine - Advanced optimization using quantum computing principles
"""
import json
import logging
import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import random
from scipy.optimize import differential_evolution
from scipy.spatial.distance import euclidean

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of optimization problems"""
    COMBINATORIAL = "combinatorial"
    CONTINUOUS = "continuous"
    MULTI_OBJECTIVE = "multi_objective"
    DYNAMIC = "dynamic"
    STOCHASTIC = "stochastic"
    CONSTRAINED = "constrained"


class QuantumState(Enum):
    """Quantum states for optimization"""
    SUPERPOSITION = "superposition"
    ENTANGLED = "entangled"
    COHERENT = "coherent"
    DECOHERENT = "decoherent"


@dataclass
class OptimizationProblem:
    """Definition of optimization problem"""
    name: str
    type: OptimizationType
    objective_functions: List[str]
    variables: Dict[str, Dict[str, Any]]
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    bounds: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    optimization_target: str = "minimize"  # minimize or maximize
    max_iterations: int = 1000
    convergence_threshold: float = 1e-6


@dataclass
class QuantumParameters:
    """Quantum-inspired parameters"""
    num_qubits: int = 10
    superposition_coefficient: float = 0.8
    entanglement_strength: float = 0.6
    coherence_time: float = 100.0
    decoherence_rate: float = 0.01
    tunneling_probability: float = 0.1
    measurement_frequency: int = 10


@dataclass
class OptimizationResult:
    """Result of optimization process"""
    best_solution: Dict[str, float]
    best_fitness: float
    convergence_history: List[float]
    optimization_time: float
    iterations_used: int
    quantum_metrics: Dict[str, Any]
    solution_quality: float
    alternative_solutions: List[Dict[str, float]]
    metadata: Dict[str, Any] = field(default_factory=dict)


class QuantumOptimizer(ABC):
    """Abstract base for quantum-inspired optimizers"""
    
    @abstractmethod
    async def optimize(self, problem: OptimizationProblem, quantum_params: QuantumParameters) -> OptimizationResult:
        """Execute quantum-inspired optimization"""
        pass


class QuantumAnnealingOptimizer(QuantumOptimizer):
    """Quantum annealing-inspired optimizer"""
    
    async def optimize(self, problem: OptimizationProblem, quantum_params: QuantumParameters) -> OptimizationResult:
        """Execute quantum annealing optimization"""
        
        start_time = datetime.now()
        
        # Initialize quantum state
        quantum_state = self._initialize_quantum_state(problem, quantum_params)
        
        # Simulated quantum annealing process
        current_solution = self._generate_initial_solution(problem)
        current_energy = self._calculate_energy(current_solution, problem)
        
        best_solution = current_solution.copy()
        best_energy = current_energy
        
        convergence_history = [current_energy]
        
        # Annealing schedule
        temperature = 1.0
        cooling_rate = 0.95
        
        for iteration in range(problem.max_iterations):
            # Quantum tunneling and superposition exploration
            candidate_solution = self._quantum_tunneling_step(
                current_solution, temperature, quantum_params, problem
            )
            
            candidate_energy = self._calculate_energy(candidate_solution, problem)
            
            # Quantum acceptance criterion
            delta_energy = candidate_energy - current_energy
            acceptance_prob = self._quantum_acceptance_probability(
                delta_energy, temperature, quantum_params
            )
            
            if random.random() < acceptance_prob:
                current_solution = candidate_solution
                current_energy = candidate_energy
                
                if current_energy < best_energy:
                    best_solution = current_solution.copy()
                    best_energy = current_energy
            
            convergence_history.append(best_energy)
            
            # Cool down
            temperature *= cooling_rate
            
            # Check convergence
            if len(convergence_history) > 50:
                recent_variance = np.var(convergence_history[-50:])
                if recent_variance < problem.convergence_threshold:
                    break
        
        optimization_time = (datetime.now() - start_time).total_seconds()
        
        # Calculate quantum metrics
        quantum_metrics = self._calculate_quantum_metrics(
            quantum_state, iteration, temperature, quantum_params
        )
        
        # Generate alternative solutions
        alternative_solutions = self._generate_alternative_solutions(
            best_solution, problem, quantum_params
        )
        
        return OptimizationResult(
            best_solution=best_solution,
            best_fitness=best_energy,
            convergence_history=convergence_history,
            optimization_time=optimization_time,
            iterations_used=iteration + 1,
            quantum_metrics=quantum_metrics,
            solution_quality=self._calculate_solution_quality(best_energy, convergence_history),
            alternative_solutions=alternative_solutions,
            metadata={"optimizer": "quantum_annealing", "final_temperature": temperature}
        )
    
    def _initialize_quantum_state(self, problem: OptimizationProblem, params: QuantumParameters) -> Dict[str, Any]:
        """Initialize quantum state for optimization"""
        return {
            "state": QuantumState.SUPERPOSITION,
            "amplitudes": np.random.uniform(-1, 1, params.num_qubits),
            "phase": np.random.uniform(0, 2*np.pi, params.num_qubits),
            "coherence": 1.0
        }
    
    def _generate_initial_solution(self, problem: OptimizationProblem) -> Dict[str, float]:
        """Generate initial solution"""
        solution = {}
        for var_name, var_config in problem.variables.items():
            if var_config["type"] == "continuous":
                bounds = problem.bounds.get(var_name, (0, 1))
                solution[var_name] = random.uniform(bounds[0], bounds[1])
            elif var_config["type"] == "discrete":
                values = var_config["values"]
                solution[var_name] = random.choice(values)
            elif var_config["type"] == "binary":
                solution[var_name] = random.choice([0, 1])
        return solution
    
    def _calculate_energy(self, solution: Dict[str, float], problem: OptimizationProblem) -> float:
        """Calculate energy (objective function value) of solution"""
        # Simulated objective function calculation
        energy = 0.0
        
        for obj_func in problem.objective_functions:
            if obj_func == "cost_minimization":
                energy += sum(solution.values())  # Simple cost function
            elif obj_func == "performance_maximization":
                energy -= np.mean(list(solution.values()))  # Negative for maximization
            elif obj_func == "balance_optimization":
                values = list(solution.values())
                energy += np.var(values)  # Minimize variance for balance
        
        return energy
    
    def _quantum_tunneling_step(
        self,
        current_solution: Dict[str, float],
        temperature: float,
        params: QuantumParameters,
        problem: OptimizationProblem
    ) -> Dict[str, float]:
        """Perform quantum tunneling step"""
        
        new_solution = current_solution.copy()
        
        # Quantum superposition exploration
        if random.random() < params.superposition_coefficient:
            # Explore multiple states simultaneously
            for var_name in new_solution:
                if random.random() < params.tunneling_probability:
                    if problem.variables[var_name]["type"] == "continuous":
                        bounds = problem.bounds.get(var_name, (0, 1))
                        # Quantum tunneling jump
                        jump_size = temperature * np.random.randn()
                        new_solution[var_name] += jump_size
                        new_solution[var_name] = np.clip(new_solution[var_name], bounds[0], bounds[1])
        
        return new_solution
    
    def _quantum_acceptance_probability(
        self,
        delta_energy: float,
        temperature: float,
        params: QuantumParameters
    ) -> float:
        """Calculate quantum acceptance probability"""
        
        # Quantum-enhanced Metropolis criterion
        if delta_energy < 0:
            return 1.0
        
        # Include quantum tunneling effects
        thermal_prob = np.exp(-delta_energy / temperature)
        tunneling_prob = params.tunneling_probability * np.exp(-delta_energy / (temperature * 0.1))
        
        return min(1.0, thermal_prob + tunneling_prob)
    
    def _calculate_quantum_metrics(
        self,
        quantum_state: Dict[str, Any],
        iterations: int,
        temperature: float,
        params: QuantumParameters
    ) -> Dict[str, Any]:
        """Calculate quantum performance metrics"""
        
        return {
            "final_coherence": quantum_state["coherence"] * np.exp(-params.decoherence_rate * iterations),
            "entanglement_entropy": self._calculate_entanglement_entropy(quantum_state),
            "quantum_speedup": iterations / params.num_qubits,
            "tunneling_events": int(iterations * params.tunneling_probability),
            "final_temperature": temperature,
            "coherence_preservation": quantum_state["coherence"] > 0.5
        }
    
    def _calculate_entanglement_entropy(self, quantum_state: Dict[str, Any]) -> float:
        """Calculate quantum entanglement entropy"""
        amplitudes = quantum_state["amplitudes"]
        probabilities = np.abs(amplitudes) ** 2
        probabilities = probabilities / np.sum(probabilities)  # Normalize
        
        # Von Neumann entropy
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return entropy
    
    def _generate_alternative_solutions(
        self,
        best_solution: Dict[str, float],
        problem: OptimizationProblem,
        params: QuantumParameters
    ) -> List[Dict[str, float]]:
        """Generate alternative near-optimal solutions"""
        
        alternatives = []
        for i in range(5):  # Generate 5 alternatives
            alternative = best_solution.copy()
            
            # Small quantum perturbations
            for var_name in alternative:
                if random.random() < 0.3:  # 30% chance to modify each variable
                    if problem.variables[var_name]["type"] == "continuous":
                        bounds = problem.bounds.get(var_name, (0, 1))
                        perturbation = np.random.normal(0, 0.1 * (bounds[1] - bounds[0]))
                        alternative[var_name] += perturbation
                        alternative[var_name] = np.clip(alternative[var_name], bounds[0], bounds[1])
            
            alternatives.append(alternative)
        
        return alternatives
    
    def _calculate_solution_quality(self, best_energy: float, convergence_history: List[float]) -> float:
        """Calculate quality of solution"""
        if not convergence_history:
            return 0.0
        
        # Quality based on convergence and final energy
        convergence_rate = (convergence_history[0] - best_energy) / max(1, len(convergence_history))
        stability = 1.0 - np.var(convergence_history[-10:]) / (np.var(convergence_history) + 1e-10)
        
        return min(1.0, (convergence_rate + stability) / 2)


class QuantumGeneticOptimizer(QuantumOptimizer):
    """Quantum-inspired genetic algorithm optimizer"""
    
    async def optimize(self, problem: OptimizationProblem, quantum_params: QuantumParameters) -> OptimizationResult:
        """Execute quantum genetic optimization"""
        
        start_time = datetime.now()
        
        # Initialize quantum population
        population = self._initialize_quantum_population(problem, quantum_params)
        
        best_solution = None
        best_fitness = float('inf')
        convergence_history = []
        
        for generation in range(problem.max_iterations):
            # Quantum evaluation
            fitness_scores = []
            for individual in population:
                fitness = self._calculate_fitness(individual, problem)
                fitness_scores.append(fitness)
                
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_solution = individual.copy()
            
            convergence_history.append(best_fitness)
            
            # Quantum selection and reproduction
            population = self._quantum_selection_reproduction(
                population, fitness_scores, quantum_params, problem
            )
            
            # Quantum crossover and mutation
            population = self._quantum_crossover_mutation(
                population, quantum_params, problem
            )
            
            # Check convergence
            if len(convergence_history) > 20:
                recent_improvement = convergence_history[-20] - convergence_history[-1]
                if recent_improvement < problem.convergence_threshold:
                    break
        
        optimization_time = (datetime.now() - start_time).total_seconds()
        
        return OptimizationResult(
            best_solution=best_solution or {},
            best_fitness=best_fitness,
            convergence_history=convergence_history,
            optimization_time=optimization_time,
            iterations_used=generation + 1,
            quantum_metrics={"generations": generation + 1, "population_size": len(population)},
            solution_quality=self._calculate_solution_quality(best_fitness, convergence_history),
            alternative_solutions=population[:5],  # Top 5 individuals
            metadata={"optimizer": "quantum_genetic"}
        )
    
    def _initialize_quantum_population(self, problem: OptimizationProblem, params: QuantumParameters) -> List[Dict[str, float]]:
        """Initialize quantum population with superposition states"""
        
        population_size = params.num_qubits * 2
        population = []
        
        for _ in range(population_size):
            individual = {}
            for var_name, var_config in problem.variables.items():
                if var_config["type"] == "continuous":
                    bounds = problem.bounds.get(var_name, (0, 1))
                    # Quantum superposition: weighted average of multiple states
                    num_states = random.randint(2, 5)
                    states = [random.uniform(bounds[0], bounds[1]) for _ in range(num_states)]
                    weights = np.random.dirichlet(np.ones(num_states))
                    individual[var_name] = np.sum(states * weights)
                elif var_config["type"] == "discrete":
                    values = var_config["values"]
                    individual[var_name] = random.choice(values)
                elif var_config["type"] == "binary":
                    individual[var_name] = random.choice([0, 1])
            
            population.append(individual)
        
        return population
    
    def _calculate_fitness(self, individual: Dict[str, float], problem: OptimizationProblem) -> float:
        """Calculate fitness of individual"""
        # Similar to energy calculation but for genetic algorithm
        fitness = 0.0
        
        for obj_func in problem.objective_functions:
            if obj_func == "cost_minimization":
                fitness += sum(individual.values())
            elif obj_func == "performance_maximization":
                fitness -= np.mean(list(individual.values()))
            elif obj_func == "balance_optimization":
                values = list(individual.values())
                fitness += np.var(values)
        
        return fitness
    
    def _quantum_selection_reproduction(
        self,
        population: List[Dict[str, float]],
        fitness_scores: List[float],
        params: QuantumParameters,
        problem: OptimizationProblem
    ) -> List[Dict[str, float]]:
        """Quantum-inspired selection and reproduction"""
        
        # Quantum tournament selection with entanglement
        new_population = []
        population_size = len(population)
        
        for _ in range(population_size):
            # Select parents with quantum entanglement consideration
            parent1_idx = self._quantum_tournament_selection(fitness_scores, params)
            parent2_idx = self._quantum_tournament_selection(fitness_scores, params)
            
            parent1 = population[parent1_idx]
            parent2 = population[parent2_idx]
            
            # Quantum reproduction
            child = self._quantum_reproduction(parent1, parent2, params)
            new_population.append(child)
        
        return new_population
    
    def _quantum_tournament_selection(self, fitness_scores: List[float], params: QuantumParameters) -> int:
        """Quantum tournament selection"""
        
        tournament_size = max(2, len(fitness_scores) // 4)
        tournament_indices = random.sample(range(len(fitness_scores)), tournament_size)
        
        # Quantum evaluation of tournament participants
        best_idx = None
        best_fitness = float('inf')
        
        for idx in tournament_indices:
            # Apply quantum phase to fitness
            quantum_fitness = fitness_scores[idx] * (1 + params.entanglement_strength * np.random.randn())
            
            if quantum_fitness < best_fitness:
                best_fitness = quantum_fitness
                best_idx = idx
        
        return best_idx
    
    def _quantum_reproduction(
        self,
        parent1: Dict[str, float],
        parent2: Dict[str, float],
        params: QuantumParameters
    ) -> Dict[str, float]:
        """Quantum reproduction with superposition"""
        
        child = {}
        
        for var_name in parent1.keys():
            # Quantum superposition of parents
            alpha = random.random()  # Superposition coefficient
            
            if random.random() < params.superposition_coefficient:
                # Quantum superposition
                child[var_name] = alpha * parent1[var_name] + (1 - alpha) * parent2[var_name]
            else:
                # Classical inheritance
                child[var_name] = parent1[var_name] if random.random() < 0.5 else parent2[var_name]
        
        return child
    
    def _quantum_crossover_mutation(
        self,
        population: List[Dict[str, float]],
        params: QuantumParameters,
        problem: OptimizationProblem
    ) -> List[Dict[str, float]]:
        """Quantum crossover and mutation"""
        
        for i in range(len(population)):
            individual = population[i]
            
            # Quantum mutation
            for var_name in individual:
                if random.random() < params.decoherence_rate:
                    if problem.variables[var_name]["type"] == "continuous":
                        bounds = problem.bounds.get(var_name, (0, 1))
                        # Quantum tunneling mutation
                        mutation = random.gauss(0, 0.1 * (bounds[1] - bounds[0]))
                        individual[var_name] += mutation
                        individual[var_name] = np.clip(individual[var_name], bounds[0], bounds[1])
        
        return population
    
    def _calculate_solution_quality(self, best_fitness: float, convergence_history: List[float]) -> float:
        """Calculate quality of solution"""
        if not convergence_history:
            return 0.0
        
        improvement = (convergence_history[0] - best_fitness) / max(1, convergence_history[0])
        return min(1.0, improvement)


class QuantumParticleSwarmOptimizer(QuantumOptimizer):
    """Quantum-inspired particle swarm optimizer"""
    
    async def optimize(self, problem: OptimizationProblem, quantum_params: QuantumParameters) -> OptimizationResult:
        """Execute quantum particle swarm optimization"""
        
        start_time = datetime.now()
        
        # Initialize quantum swarm
        swarm = self._initialize_quantum_swarm(problem, quantum_params)
        personal_best = [particle.copy() for particle in swarm]
        global_best = min(swarm, key=lambda x: self._calculate_fitness(x, problem))
        
        convergence_history = []
        
        for iteration in range(problem.max_iterations):
            # Update quantum velocities and positions
            for i, particle in enumerate(swarm):
                # Quantum velocity update
                velocity = self._calculate_quantum_velocity(
                    particle, personal_best[i], global_best, quantum_params
                )
                
                # Update position with quantum behavior
                swarm[i] = self._update_quantum_position(particle, velocity, problem, quantum_params)
                
                # Update personal best
                current_fitness = self._calculate_fitness(swarm[i], problem)
                personal_best_fitness = self._calculate_fitness(personal_best[i], problem)
                
                if current_fitness < personal_best_fitness:
                    personal_best[i] = swarm[i].copy()
                
                # Update global best
                if current_fitness < self._calculate_fitness(global_best, problem):
                    global_best = swarm[i].copy()
            
            convergence_history.append(self._calculate_fitness(global_best, problem))
            
            # Check convergence
            if len(convergence_history) > 30:
                recent_variance = np.var(convergence_history[-30:])
                if recent_variance < problem.convergence_threshold:
                    break
        
        optimization_time = (datetime.now() - start_time).total_seconds()
        
        return OptimizationResult(
            best_solution=global_best,
            best_fitness=self._calculate_fitness(global_best, problem),
            convergence_history=convergence_history,
            optimization_time=optimization_time,
            iterations_used=iteration + 1,
            quantum_metrics={"swarm_size": len(swarm), "quantum_convergence": iteration},
            solution_quality=self._calculate_solution_quality(
                self._calculate_fitness(global_best, problem), convergence_history
            ),
            alternative_solutions=personal_best[:5],
            metadata={"optimizer": "quantum_particle_swarm"}
        )
    
    def _initialize_quantum_swarm(self, problem: OptimizationProblem, params: QuantumParameters) -> List[Dict[str, float]]:
        """Initialize quantum particle swarm"""
        
        swarm_size = params.num_qubits
        swarm = []
        
        for _ in range(swarm_size):
            particle = {}
            for var_name, var_config in problem.variables.items():
                if var_config["type"] == "continuous":
                    bounds = problem.bounds.get(var_name, (0, 1))
                    # Quantum position with uncertainty
                    mean_pos = random.uniform(bounds[0], bounds[1])
                    particle[var_name] = mean_pos + random.gauss(0, 0.1 * (bounds[1] - bounds[0]))
                    particle[var_name] = np.clip(particle[var_name], bounds[0], bounds[1])
                else:
                    # Handle other variable types
                    if var_config["type"] == "discrete":
                        particle[var_name] = random.choice(var_config["values"])
                    elif var_config["type"] == "binary":
                        particle[var_name] = random.choice([0, 1])
            
            swarm.append(particle)
        
        return swarm
    
    def _calculate_quantum_velocity(
        self,
        particle: Dict[str, float],
        personal_best: Dict[str, float],
        global_best: Dict[str, float],
        params: QuantumParameters
    ) -> Dict[str, float]:
        """Calculate quantum velocity"""
        
        velocity = {}
        
        for var_name in particle.keys():
            # Quantum velocity components
            inertia = 0.7  # Inertia weight
            cognitive = 1.5  # Cognitive coefficient
            social = 1.5  # Social coefficient
            
            # Add quantum randomness
            quantum_factor = params.entanglement_strength * random.gauss(0, 1)
            
            # Calculate velocity component
            r1, r2 = random.random(), random.random()
            
            velocity[var_name] = (
                inertia * 0 +  # Previous velocity (simplified)
                cognitive * r1 * (personal_best[var_name] - particle[var_name]) +
                social * r2 * (global_best[var_name] - particle[var_name]) +
                quantum_factor
            )
        
        return velocity
    
    def _update_quantum_position(
        self,
        particle: Dict[str, float],
        velocity: Dict[str, float],
        problem: OptimizationProblem,
        params: QuantumParameters
    ) -> Dict[str, float]:
        """Update quantum particle position"""
        
        new_position = particle.copy()
        
        for var_name in particle.keys():
            if problem.variables[var_name]["type"] == "continuous":
                # Update position with quantum behavior
                new_position[var_name] += velocity[var_name]
                
                # Apply quantum tunneling with probability
                if random.random() < params.tunneling_probability:
                    bounds = problem.bounds.get(var_name, (0, 1))
                    tunnel_jump = random.gauss(0, 0.2 * (bounds[1] - bounds[0]))
                    new_position[var_name] += tunnel_jump
                
                # Apply bounds
                bounds = problem.bounds.get(var_name, (0, 1))
                new_position[var_name] = np.clip(new_position[var_name], bounds[0], bounds[1])
        
        return new_position
    
    def _calculate_fitness(self, individual: Dict[str, float], problem: OptimizationProblem) -> float:
        """Calculate fitness of individual"""
        fitness = 0.0
        
        for obj_func in problem.objective_functions:
            if obj_func == "cost_minimization":
                fitness += sum(individual.values())
            elif obj_func == "performance_maximization":
                fitness -= np.mean(list(individual.values()))
            elif obj_func == "balance_optimization":
                values = list(individual.values())
                fitness += np.var(values)
        
        return fitness
    
    def _calculate_solution_quality(self, best_fitness: float, convergence_history: List[float]) -> float:
        """Calculate quality of solution"""
        if not convergence_history:
            return 0.0
        
        improvement = (convergence_history[0] - best_fitness) / max(1, convergence_history[0])
        return min(1.0, improvement)


class QuantumOptimizationEngine:
    """Main quantum optimization engine with multiple algorithms"""
    
    def __init__(self):
        self.optimizers = {
            "annealing": QuantumAnnealingOptimizer(),
            "genetic": QuantumGeneticOptimizer(),
            "particle_swarm": QuantumParticleSwarmOptimizer()
        }
        self.optimization_history = []
        self.performance_metrics = {
            "total_optimizations": 0,
            "average_optimization_time": 0.0,
            "success_rate": 0.0,
            "most_used_algorithm": None
        }
    
    async def optimize(
        self,
        problem: OptimizationProblem,
        algorithm: str = "auto",
        quantum_params: Optional[QuantumParameters] = None,
        enable_ensemble: bool = False
    ) -> Union[OptimizationResult, Dict[str, OptimizationResult]]:
        """Execute quantum optimization"""
        
        if quantum_params is None:
            quantum_params = QuantumParameters()
        
        start_time = datetime.now()
        
        try:
            if enable_ensemble:
                # Run all algorithms and ensemble results
                results = {}
                for algo_name, optimizer in self.optimizers.items():
                    result = await optimizer.optimize(problem, quantum_params)
                    results[algo_name] = result
                
                # Generate ensemble result
                ensemble_result = self._generate_ensemble_result(results, problem)
                results["ensemble"] = ensemble_result
                
                final_result = results
                
            else:
                # Auto-select best algorithm or use specified one
                if algorithm == "auto":
                    algorithm = self._select_best_algorithm(problem)
                
                optimizer = self.optimizers[algorithm]
                final_result = await optimizer.optimize(problem, quantum_params)
            
            # Update metrics
            self._update_metrics(algorithm, final_result, start_time)
            
            # Record optimization
            self.optimization_history.append({
                "timestamp": start_time,
                "problem": problem.name,
                "algorithm": algorithm,
                "success": True,
                "optimization_time": (datetime.now() - start_time).total_seconds(),
                "best_fitness": final_result.best_fitness if not enable_ensemble else final_result["ensemble"].best_fitness
            })
            
            return final_result
            
        except Exception as e:
            logger.error(f"Quantum optimization failed: {str(e)}")
            
            # Record failure
            self.optimization_history.append({
                "timestamp": start_time,
                "problem": problem.name,
                "algorithm": algorithm,
                "success": False,
                "error": str(e)
            })
            
            raise
    
    def _select_best_algorithm(self, problem: OptimizationProblem) -> str:
        """Auto-select best algorithm based on problem characteristics"""
        
        if problem.type == OptimizationType.COMBINATORIAL:
            return "genetic"
        elif problem.type == OptimizationType.CONTINUOUS:
            return "annealing"
        elif problem.type == OptimizationType.MULTI_OBJECTIVE:
            return "particle_swarm"
        else:
            return "annealing"  # Default
    
    def _generate_ensemble_result(
        self,
        results: Dict[str, OptimizationResult],
        problem: OptimizationProblem
    ) -> OptimizationResult:
        """Generate ensemble result from multiple algorithms"""
        
        if not results:
            raise ValueError("No results to ensemble")
        
        # Find best result across all algorithms
        best_result = None
        best_fitness = float('inf')
        
        for result in results.values():
            if result.best_fitness < best_fitness:
                best_fitness = result.best_fitness
                best_result = result
        
        # Combine convergence histories
        all_histories = [r.convergence_history for r in results.values()]
        max_length = max(len(h) for h in all_histories)
        
        ensemble_history = []
        for i in range(max_length):
            values = []
            for h in all_histories:
                if i < len(h):
                    values.append(h[i])
            ensemble_history.append(np.mean(values) if values else best_fitness)
        
        # Combine quantum metrics
        ensemble_quantum_metrics = {
            "ensemble_size": len(results),
            "algorithm_performance": {name: r.quantum_metrics for name, r in results.items()},
            "best_algorithm": best_result.metadata.get("optimizer", "unknown")
        }
        
        # Combine alternative solutions
        all_alternatives = []
        for result in results.values():
            all_alternatives.extend(result.alternative_solutions)
        
        # Remove duplicates and keep top ones
        unique_alternatives = []
        seen = set()
        for alt in all_alternatives:
            alt_tuple = tuple(sorted(alt.items()))
            if alt_tuple not in seen:
                seen.add(alt_tuple)
                unique_alternatives.append(alt)
        
        return OptimizationResult(
            best_solution=best_result.best_solution,
            best_fitness=best_result.best_fitness,
            convergence_history=ensemble_history,
            optimization_time=sum(r.optimization_time for r in results.values()),
            iterations_used=max(r.iterations_used for r in results.values()),
            quantum_metrics=ensemble_quantum_metrics,
            solution_quality=self._calculate_ensemble_quality(results),
            alternative_solutions=unique_alternatives[:10],  # Top 10 alternatives
            metadata={
                "ensemble_method": "best_fitness_selection",
                "algorithms_used": list(results.keys()),
                "ensemble_size": len(results)
            }
        )
    
    def _calculate_ensemble_quality(self, results: Dict[str, OptimizationResult]) -> float:
        """Calculate quality of ensemble result"""
        if not results:
            return 0.0
        
        qualities = [r.solution_quality for r in results.values()]
        return np.mean(qualities)
    
    def _update_metrics(self, algorithm: str, result: Union[OptimizationResult, Dict], start_time: datetime):
        """Update performance metrics"""
        self.performance_metrics["total_optimizations"] += 1
        
        # Update average optimization time
        opt_time = (datetime.now() - start_time).total_seconds()
        total_opts = self.performance_metrics["total_optimizations"]
        current_avg = self.performance_metrics["average_optimization_time"]
        self.performance_metrics["average_optimization_time"] = (
            (current_avg * (total_opts - 1) + opt_time) / total_opts
        )
        
        # Update success rate
        successful = sum(1 for opt in self.optimization_history if opt["success"])
        self.performance_metrics["success_rate"] = successful / total_opts
        
        # Track most used algorithm
        self.performance_metrics["most_used_algorithm"] = algorithm
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            "metrics": self.performance_metrics,
            "recent_optimizations": self.optimization_history[-10:],
            "algorithm_usage": self._analyze_algorithm_usage(),
            "performance_trends": self._analyze_performance_trends()
        }
    
    def _analyze_algorithm_usage(self) -> Dict[str, int]:
        """Analyze usage patterns of different algorithms"""
        usage = {}
        for opt in self.optimization_history:
            if opt["success"]:
                algo = opt["algorithm"]
                usage[algo] = usage.get(algo, 0) + 1
        return usage
    
    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if len(self.optimization_history) < 2:
            return {"trend": "insufficient_data"}
        
        recent_opts = [opt for opt in self.optimization_history[-10:] if opt["success"]]
        older_opts = [opt for opt in self.optimization_history[-20:-10] if opt["success"]]
        
        if not recent_opts or not older_opts:
            return {"trend": "insufficient_success_data"}
        
        recent_avg_time = np.mean([opt["optimization_time"] for opt in recent_opts])
        older_avg_time = np.mean([opt["optimization_time"] for opt in older_opts])
        
        trend = "improving" if recent_avg_time < older_avg_time else "declining" if recent_avg_time > older_avg_time else "stable"
        
        return {
            "trend": trend,
            "recent_average_time": recent_avg_time,
            "older_average_time": older_avg_time,
            "improvement": older_avg_time - recent_avg_time
        }
    
    async def multi_objective_optimize(
        self,
        problems: List[OptimizationProblem],
        quantum_params: Optional[QuantumParameters] = None
    ) -> Dict[str, OptimizationResult]:
        """Optimize multiple objectives simultaneously"""
        
        if quantum_params is None:
            quantum_params = QuantumParameters()
        
        results = {}
        
        # Optimize each problem
        for problem in problems:
            result = await self.optimize(problem, "auto", quantum_params, False)
            results[problem.name] = result
        
        # Find Pareto optimal solutions
        pareto_solutions = self._find_pareto_optimal_solutions(results)
        
        return {
            "individual_results": results,
            "pareto_optimal": pareto_solutions,
            "trade_off_analysis": self._analyze_trade_offs(results)
        }
    
    def _find_pareto_optimal_solutions(self, results: Dict[str, OptimizationResult]) -> List[Dict[str, Any]]:
        """Find Pareto optimal solutions from multi-objective optimization"""
        
        # Convert results to objective space
        objectives = []
        solutions = []
        
        for name, result in results.items():
            objectives.append(result.best_fitness)
            solutions.append({
                "name": name,
                "solution": result.best_solution,
                "fitness": result.best_fitness,
                "quality": result.solution_quality
            })
        
        # Find Pareto front (simplified)
        pareto_optimal = []
        
        for i, sol in enumerate(solutions):
            is_pareto = True
            for j, other in enumerate(solutions):
                if i != j and other["fitness"] < sol["fitness"] and other["quality"] >= sol["quality"]:
                    is_pareto = False
                    break
            
            if is_pareto:
                pareto_optimal.append(sol)
        
        return pareto_optimal
    
    def _analyze_trade_offs(self, results: Dict[str, OptimizationResult]) -> Dict[str, Any]:
        """Analyze trade-offs between different objectives"""
        
        trade_offs = {}
        
        for name1, result1 in results.items():
            for name2, result2 in results.items():
                if name1 != name2:
                    trade_off_key = f"{name1}_vs_{name2}"
                    trade_offs[trade_off_key] = {
                        "fitness_difference": result2.best_fitness - result1.best_fitness,
                        "quality_difference": result2.solution_quality - result1.solution_quality,
                        "time_difference": result2.optimization_time - result1.optimization_time
                    }
        
        return trade_offs


# Create singleton instance
quantum_optimization_engine = QuantumOptimizationEngine()
