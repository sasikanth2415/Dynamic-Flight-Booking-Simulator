import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api";

export default function SeatSelection() {
  const { flightId } = useParams();
  const [seats, setSeats] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    api.get(`/flights/${flightId}/seats/`)
      .then((res) => setSeats(res.data))
      .catch(() => alert("Error loading seats"));
  }, [flightId]);

  return (
    <div>
      <h2>Select a Seat</h2>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center" }}>
        {seats.map((s) => (
          <button
            key={s.id}
            disabled={s.is_booked}
            onClick={() => navigate(`/quote/${flightId}/${s.id}`)}
            style={{
              margin: "5px",
              padding: "10px",
              backgroundColor: s.is_booked ? "#ccc" : "#007bff",
              color: "#fff",
            }}
          >
            {s.seat_number} ({s.seat_class})
          </button>
        ))}
      </div>
    </div>
  );
}
