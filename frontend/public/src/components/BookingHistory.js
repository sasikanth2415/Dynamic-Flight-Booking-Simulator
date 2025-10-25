import React, { useEffect, useState } from "react";
import { api } from "../api";

export default function BookingHistory() {
  const [bookings, setBookings] = useState([]);

  useEffect(() => {
    api.get("/bookings/history/").then((res) => setBookings(res.data));
  }, []);

  const cancelBooking = async (id) => {
    await api.post(`/booking/${id}/cancel/`);
    setBookings(bookings.filter((b) => b.id !== id));
  };

  return (
    <div>
      <h2>Booking History</h2>
      <table border="1" style={{ margin: "auto" }}>
        <thead>
          <tr>
            <th>PNR</th>
            <th>Passenger</th>
            <th>Flight</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {bookings.map((b) => (
            <tr key={b.id}>
              <td>{b.confirmation_code}</td>
              <td>{b.passenger_name}</td>
              <td>{b.flight_number}</td>
              <td>{b.status}</td>
              <td>
                {b.status !== "cancelled" && (
                  <button onClick={() => cancelBooking(b.id)}>Cancel</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
