from collections import defaultdict
import numpy as np

# ========== INPUTS ========== #

# The maximum number of lives that can be held at a time.
MAX_LIVES = 9

# The number of lives at the start of a run.
LIVES = 5

# The list of sections of the game, each with cap rates,
# time needed to complete the section, and lives gained after completing the section.
SECTIONS = [
    {"rate": 0.98, "time": 0.4, "life_gain": 0},
    {"rate": 0.92, "time": 0.4, "life_gain": 0},
    {"rate": 0.80, "time": 0.5, "life_gain": 1},
    {"rate": 0.40, "time": 0.3, "life_gain": 0},
    {"rate": 0.59, "time": 0.7, "life_gain": 0},
    {"rate": 0.25, "time": 0.5, "life_gain": 1},
    {"rate": 0.63, "time": 0.4, "life_gain": 0},
    {"rate": 0.44, "time": 0.6, "life_gain": 0},
]

# The number of times to "simulate" going from one section to another.
# This can also be thought of as the simulation/calculation depth.
# Increasing this number will make the result more accurate but take longer to compute.
TRANSITIONS = 200

# ============================ #

# Calculate the maximum number of lives that can be had at any point in the run.
# This reduces the simulation state space to only what is needed to calculate the answer.
max_simulation_lives = min(LIVES + sum([gain for section in SECTIONS if (gain := section["life_gain"]) > 0]), MAX_LIVES)

# The cap rate in each section is taken to be the probability of not losing any lives in that section.
# We assume the existence of a "single miss rate": the probability of losing one life in a section.
# We also assume events where lives are lost are independent of each other;
# P(n lives lost) = single miss rate ^ n.
# Let r be the cap rate and s be the single miss rate. Then, s + s^2 + s^3 + ... = 1 - r.
# By telescoping, we find s = (1 - r)/(2 - r).
section_miss_rates = [
    (1.0 - section["rate"]) / (2.0 - section["rate"]) for section in SECTIONS
]

assert LIVES > 0
assert len(SECTIONS) > 0
assert TRANSITIONS >= 0


# Returns the PDF of run success (i.e. all sections cleared) over time.
# The index of the starting section and number of lives can be customized.
def pdf(init_section, init_lives):
    assert 0 <= init_section <= len(SECTIONS) - 1
    assert 1 <= init_lives <= LIVES

    pdist = defaultdict(float)

    state = defaultdict(lambda: np.zeros((len(SECTIONS) + 1, max_simulation_lives)))
    new_state = defaultdict(lambda: np.zeros((len(SECTIONS) + 1, max_simulation_lives)))

    # Recursion base case
    state[0.0][init_section][init_lives - 1] = 1.0

    for _ in range(TRANSITIONS):
        for time, probs in state.items():
            for s_idx, section in enumerate(SECTIONS):
                new_time_complete = round(time + section["time"], 2)
                new_time_incomplete = round(time + section["time"] / 2, 2)

                for life_count in range(max_simulation_lives):
                    old_prob = probs[s_idx][life_count]
                    prob_some_lives_lost = 0.0

                    # Section cleared; no lives lost
                    new_life_count = min(life_count + section["life_gain"], max_simulation_lives - 1)
                    new_state[new_time_complete][s_idx + 1][new_life_count] += old_prob * section["rate"]

                    # Section cleared; some lives lost
                    for lost_life_count in range(1, life_count):
                        prob_lost_life_count = section_miss_rates[s_idx] ** lost_life_count
                        prob_some_lives_lost += prob_lost_life_count
                        new_life_count = min(life_count - lost_life_count + section["life_gain"], max_simulation_lives - 1)
                        new_state[new_time_complete][s_idx][new_life_count] += old_prob * prob_lost_life_count

                    # Section not cleared; all lives lost
                    # We assume that, if we lose during a section, we spend half of the time needed to complete the section.
                    new_state[new_time_incomplete][0][LIVES - 1] += old_prob * (1.0 - section["rate"] - prob_some_lives_lost)

        state = new_state
        new_state = defaultdict(lambda: np.zeros((len(SECTIONS) + 1, max_simulation_lives)))

        # Update the probability distribution with times and probabilities of
        # states where all sections were cleared successfully
        for time, probs in state.items():
            pdist[time] += sum(probs[-1][:])

    return pdist


def process_pdist(pdist):
    # Sort pdist by time in increasing order
    data = sorted(pdist.items())

    times = [time for (time, _) in data]
    probs = [prob for (_, prob) in data]

    return times, probs


# Returns the probability that the random variable with values `t1` and probabilities `p1`
# is greater than the random variable with values `t2` and probabilities `p2`.
def prob_greater(t1, p1, t2, p2):
    assert len(t1) == len(p1) == len(t2) == len(p2)

    curr_prob = 0.0
    curr_cprob2 = 0.0
    idx2 = 0
    for time1, prob1 in zip(t1, p1):
        while idx2 < len(t2) and time1 > t2[idx2]:
            curr_cprob2 += p2[idx2]
            idx2 += 1
        curr_prob += prob1 * curr_cprob2

    return curr_prob

# Prints the probability that, given a starting section index and life count,
# restarting the run will lead to more time spent overall than continuing (and vice versa).
def main(section, lives):
    pdist_restart_times, pdist_restart_probs = process_pdist(pdf(0, LIVES))
    pdist_continue_times, pdist_continue_probs = process_pdist(pdf(section, lives))

    prob_restart_longer = prob_greater(
        pdist_restart_times,
        pdist_restart_probs,
        pdist_continue_times,
        pdist_continue_probs,
    )
    prob_continue_longer = prob_greater(
        pdist_continue_times,
        pdist_continue_probs,
        pdist_restart_times,
        pdist_restart_probs,
    )

    # `prob_restart_longer` and `prob_continue_longer` won't sum to 1 because `TRANSITIONS` is finite;
    # we can't simulate state transitions beyond that depth
    # like in cases where it takes many, many restarts before completing a run.
    # So, we scale up the probabilities such that they sum to 1.
    # Note: we assume that the probability of the two random variables being equal is negligible.
    estimation_scale_factor = 1.0 / (prob_restart_longer + prob_continue_longer)

    print(f"probability that restarting will take longer: {prob_restart_longer * estimation_scale_factor}")
    print(f"probability that continuing will take longer: {prob_continue_longer * estimation_scale_factor}")


if __name__ == "__main__":
    main(4, 5)
