import streamlit as st
import pandas as pd
import datetime
import os

# ----------------------
# Initialize Data
# ----------------------
pods = [
    {"id": 1, "name": "Single Pod 1", "capacity": 1},
    {"id": 2, "name": "Single Pod 2", "capacity": 1},
    {"id": 3, "name": "Single Pod 3", "capacity": 1},
    {"id": 4, "name": "Single Pod 4", "capacity": 1},
    {"id": 5, "name": "Single Pod 5", "capacity": 1},
    {"id": 6, "name": "Single Pod 6", "capacity": 1},
    {"id": 7, "name": "Single Pod 7", "capacity": 1},
    {"id": 8, "name": "Single Pod 8", "capacity": 1},
    {"id": 9, "name": "Double Pod 1", "capacity": 2},
    {"id": 10, "name": "Double Pod 2", "capacity": 2},
    {"id": 11, "name": "Big Pod 1", "capacity": 6},
    {"id": 12, "name": "Big Pod 2", "capacity": 6},
    {"id": 13, "name": "Big Pod 3", "capacity": 6}
]

# Load or create booking database
BOOKINGS_FILE = "bookings.csv"

if os.path.exists(BOOKINGS_FILE):
    bookings = pd.read_csv(BOOKINGS_FILE, parse_dates=['start_time', 'end_time'])
else:
    bookings = pd.DataFrame(columns=["pod_id", "pod_name", "guest_count", "start_time", "end_time", "email"])

# ----------------------
# Streamlit App
# ----------------------

st.title("PodQuest: Pod Booking System")
st.write("Easily book your office pods based on your meeting size!")

# User Input
st.header("Booking Form")
guest_count = st.number_input("Number of Guests:", min_value=1, max_value=6, step=1)

# Filter available pods
filtered_pods = [pod for pod in pods if pod["capacity"] >= guest_count]

pod_name = st.selectbox("Select a Pod:", [pod["name"] for pod in filtered_pods])

booking_date = st.date_input("Select Date:", min_value=datetime.date.today())
booking_start_time = st.time_input("Select Start Time:", value=datetime.time(9, 0))
email = st.text_input("Enter your Email:")

# Submission button
if st.button("Book Now"):
    selected_pod = next(pod for pod in pods if pod["name"] == pod_name)
    start_datetime = datetime.datetime.combine(booking_date, booking_start_time)
    end_datetime = start_datetime + datetime.timedelta(minutes=60)
    buffer_end_time = end_datetime + datetime.timedelta(minutes=10)

    # Validation: Prevent single guests from booking big pods
    if guest_count == 1 and selected_pod["capacity"] > 2:
        st.error("Single guests cannot book Big Pods. Please choose a smaller pod.")
    else:
        # Check for time conflicts
        conflict = bookings[
            (bookings["pod_id"] == selected_pod["id"]) &
            (
                ((bookings["start_time"] <= start_datetime) & (bookings["end_time"] > start_datetime)) |
                ((bookings["start_time"] < buffer_end_time) & (bookings["end_time"] >= buffer_end_time))
            )
        ]

        if not conflict.empty:
            st.error("This pod is already booked during that time. Please choose a different time or pod.")
        elif email == "":
            st.error("Please enter your email to confirm the booking.")
        else:
            # Save booking
            new_booking = pd.DataFrame([{
                "pod_id": selected_pod["id"],
                "pod_name": selected_pod["name"],
                "guest_count": guest_count,
                "start_time": start_datetime,
                "end_time": buffer_end_time,
                "email": email
            }])
            bookings = pd.concat([bookings, new_booking], ignore_index=True)
            bookings.to_csv(BOOKINGS_FILE, index=False)

            st.success(f"Booking Confirmed for {pod_name} on {booking_date} at {booking_start_time}!")
            st.info("A confirmation will be sent to your email (optional to implement)")

# ----------------------
# Admin Section
# ----------------------

st.sidebar.header("Admin: View Bookings")
if st.sidebar.checkbox("Show all bookings"):
    st.sidebar.dataframe(bookings.sort_values(by="start_time"))
