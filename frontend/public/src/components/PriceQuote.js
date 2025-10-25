import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";

export default function PriceQuote() {
  const { flightId, seatId } = useParams();
  const [age, setAge] = useState(25);
  const [luggage, setLuggage] = useState(0);
  const [price, setPrice] = useState(null);
  const navigate = useNavigate();

  const getQuote = async () => {
    try {
      const res = await api.post("/quote/price/", {
        flight_id: flightId,
        seat_id: seatId,
        passenger_age: age,
        luggage_kg: luggage,
      });
      setPrice(res.data.final_price);
    } catch {
      alert("Error fetching price");
    }
  };

  return (
    <div>
      <h2>Price Quote</h2>
      <input type="number" value={age} onChange={(e) => setAge(e.target.value)} placeholder="Passenger Age" />
      <input type="number" value={luggage} onChange={(e) => setLuggage(e.target.value)} placeholder="Luggage (kg)" />
      <button onClick={getQuote}>Get Quote</button>
      {price && (
        <div>
          <h3>Final Price: ${price}</h3>
          <button onClick={() => navigate(`/book/${flightId}/${seatId}`)}>Proceed to Book</button>
        </div>
      )}
    </div>
  );
}
