import random
import pandas as pd
import streamlit as st

# Step 1: Input Job Frequencies via UI
def get_job_data_ui():
    num_jobs = st.number_input("Enter number of jobs", min_value=1, max_value=50, value=3)
    job_data = {}
    st.subheader("Enter frequency for each job:")
    for i in range(1, num_jobs + 1):
        freq = st.number_input(f"Frequency for J{i}", min_value=1, value=10, key=f"freq_{i}")
        job_data[f"J{i}"] = freq
    return job_data

# Step 2: Create Random Number Ranges (1–99)
def create_ranges(job_data):
    total_frequency = sum(job_data.values())
    ranges = {}
    start = 1

    for job, freq in job_data.items():
        proportion = freq / total_frequency
        range_size = round(proportion * 99)
        end = start + range_size - 1
        if end > 99:
            end = 99
        ranges[job] = (start, end)
        start = end + 1

    last_job = list(ranges.keys())[-1]
    ranges[last_job] = (ranges[last_job][0], 99)

    return ranges, 99

# Step 3: Determine job from a random number
def get_job_from_random(ranges, rand_num):
    for job, (start, end) in ranges.items():
        if start <= rand_num <= end:
            return job
    return None

# Step 4: Run Simulations
def run_simulations(ranges, total_range, num_simulations, jobs_per_simulation):
    simulations = []
    job_counts = {job: 0 for job in ranges}
    simulation_details = []

    for sim in range(num_simulations):
        sequence = []
        sim_details = []
        for _ in range(jobs_per_simulation):
            rand_num = random.randint(1, total_range)
            job = get_job_from_random(ranges, rand_num)
            job_counts[job] += 1
            cumulative_prob = sum(job_counts[j] / (num_simulations * jobs_per_simulation) for j in job_counts)
            sim_details.append((rand_num, job, cumulative_prob))
            sequence.append(job)
        simulations.append(sequence)
        simulation_details.append(sim_details)

    probabilities = {job: count / (num_simulations * jobs_per_simulation) for job, count in job_counts.items()}
    cumulative_prob = {}
    cumulative_sum = 0
    for job, prob in probabilities.items():
        cumulative_sum += prob
        cumulative_prob[job] = cumulative_sum

    return simulations, probabilities, cumulative_prob, simulation_details

# Step 5: Display Results
def display_results(simulations, probabilities, cumulative_prob, simulation_details, ranges):
    st.subheader("🎯 Job Probabilities and Cumulative Probabilities")
    prob_df = pd.DataFrame({
        'Probability': probabilities,
        'Cumulative Probability': cumulative_prob
    })
    st.dataframe(prob_df.style.format({'Probability': '{:.4f}', 'Cumulative Probability': '{:.4f}'}))

    st.subheader("🔁 Simulated Job Sequences with Random Numbers")
    for i, details in enumerate(simulation_details):
        with st.expander(f"Simulation {i+1} Details"):
            detail_df = pd.DataFrame(details, columns=["Random Number", "Job", "Cumulative Probability"])
            detail_df["Range"] = detail_df["Job"].apply(lambda j: f"{ranges[j][0]}–{ranges[j][1]}")
            st.dataframe(detail_df)

    df = pd.DataFrame(simulations)
    df.index = [f"Sim {i+1}" for i in range(len(simulations))]
    st.subheader("📊 Simulated Job Sequences (Final Summary)")
    st.dataframe(df)

# Streamlit App with session state
def main():
    st.title("📌 Monte Carlo Simulation for Job Scheduling")

    # Step 1: Job Frequency Input
    if 'job_data' not in st.session_state:
        st.session_state.job_data = {}

    job_data = get_job_data_ui()

    if st.button("Generate Ranges"):
        ranges, total_range = create_ranges(job_data)
        st.session_state.job_data = job_data
        st.session_state.ranges = ranges
        st.session_state.total_range = total_range
        st.session_state.show_range = True
        st.session_state.simulations_ran = False

    # Step 2: Show ranges
    if st.session_state.get("show_range", False):
        st.subheader("📐 Generated Random Number Ranges (1–99)")
        for job, (start, end) in st.session_state.ranges.items():
            st.write(f"{job}: {start}–{end}")

        num_simulations = st.number_input("Number of simulations", min_value=1, value=50, key="num_sim")
        jobs_per_simulation = st.number_input("Jobs per simulation", min_value=1, value=29, key="jobs_per_sim")

        if st.button("🔁 Run Simulations"):
            simulations, probabilities, cumulative_prob, simulation_details = run_simulations(
                st.session_state.ranges, st.session_state.total_range, num_simulations, jobs_per_simulation
            )
            st.session_state.simulations = simulations
            st.session_state.probabilities = probabilities
            st.session_state.cumulative_prob = cumulative_prob
            st.session_state.simulation_details = simulation_details
            st.session_state.simulations_ran = True

    # Step 3: Display Results
    if st.session_state.get("simulations_ran", False):
        display_results(
            st.session_state.simulations,
            st.session_state.probabilities,
            st.session_state.cumulative_prob,
            st.session_state.simulation_details,
            st.session_state.ranges
        )

if __name__ == "__main__":
    main()
