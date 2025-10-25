import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

export default function FlightSearch() {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [date, setDate] = useState("");
  const [flights, setFlights] = useState([]);
  const navigate = useNavigate();

  const searchFlights = async () => {
    try {
      const res = await api.get("/flights/search/", {
        params: { origin, destination, date },
      });
      setFlights(res.data);
    } catch (err) {
      alert("Error fetching flights!");
    }
  };

  return (
    <div>
      <h2>Search Flights</h2>
      <input placeholder="Origin" value={origin} onChange={(e) => setOrigin(e.target.value)} />
      <input placeholder="Destination" value={destination} onChange={(e) => setDestination(e.target.value)} />
      <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
      <button onClick={searchFlights}>Search</button>

      <ul>
        {flights.map((f) => (
          <li key={f.id}>
            {f.flight_number} - {f.origin} → {f.destination}  
            <button onClick={() => navigate(`/seats/${f.id}`)}>Select Seats</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
