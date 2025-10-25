import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";

export default function BookingForm() {
  const { flightId, seatId } = useParams();
  const [name, setName] = useState("");
  const [age, setAge] = useState(25);
  const [luggage, setLuggage] = useState(0);
  const [confirmation, setConfirmation] = useState(null);

  const bookFlight = async () => {
    try {
      const res = await api.post("/book/", {
        flight_id: flightId,
        seat_id: seatId,
        passenger_name: name,
        passenger_age: age,
        luggage_kg: luggage,
      });
      setConfirmation(res.data);
    } catch {
      alert("Booking failed");
    }
  };

  return (
    <div>
      <h2>Book Flight</h2>
      <input placeholder="Passenger Name" value={name} onChange={(e) => setName(e.target.value)} />
      <input type="number" value={age} onChange={(e) => setAge(e.target.value)} placeholder="Age" />
      <input type="number" value={luggage} onChange={(e) => setLuggage(e.target.value)} placeholder="Luggage (kg)" />
      <button onClick={bookFlight}>Confirm Booking</button>

      {confirmation && (
        <div>
          <h3>✅ Booking Confirmed!</h3>
          <p>PNR: {confirmation.confirmation_code}</p>
        </div>
      )}
    </div>
  );
}
