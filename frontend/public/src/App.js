import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import FlightSearch from "./components/FlightSearch";
import SeatSelection from "./components/SeatSelection";
import PriceQuote from "./components/PriceQuote";
import BookingForm from "./components/BookingForm";
import BookingHistory from "./components/BookingHistory";

export default function App() {
  return (
    <Router>
      <div style={{ textAlign: "center", padding: "1rem" }}>
        <h1>✈️ Flight Booking Simulator</h1>
        <nav style={{ marginBottom: "1rem" }}>
          <Link to="/">Search</Link> |{" "}
          <Link to="/bookings">Bookings</Link>
        </nav>
        <Routes>
          <Route path="/" element={<FlightSearch />} />
          <Route path="/seats/:flightId" element={<SeatSelection />} />
          <Route path="/quote/:flightId/:seatId" element={<PriceQuote />} />
          <Route path="/book/:flightId/:seatId" element={<BookingForm />} />
          <Route path="/bookings" element={<BookingHistory />} />
        </Routes>
      </div>
    </Router>
  );
}
