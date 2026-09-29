import React from "react";
import "./Register.css";
import Header from "../Header/Header";

const Register = () => {
  const handleSubmit = (event) => {
    event.preventDefault();
  };

  return (
    <div>
      <Header />
      <main className="register_container">
        <h1 className="header">Sign-up</h1>
        <form onSubmit={handleSubmit}>
          <div className="inputs">
            <label className="input" htmlFor="userName">
              Username
              <input
                className="input_field"
                id="userName"
                name="userName"
                type="text"
                autoComplete="username"
                required
              />
            </label>
            <label className="input" htmlFor="firstName">
              First Name
              <input
                className="input_field"
                id="firstName"
                name="firstName"
                type="text"
                autoComplete="given-name"
                required
              />
            </label>
            <label className="input" htmlFor="lastName">
              Last Name
              <input
                className="input_field"
                id="lastName"
                name="lastName"
                type="text"
                autoComplete="family-name"
                required
              />
            </label>
            <label className="input" htmlFor="email">
              Email
              <input
                className="input_field"
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
              />
            </label>
            <label className="input" htmlFor="password">
              Password
              <input
                className="input_field"
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
              />
            </label>
          </div>
          <div className="submit_panel">
            <button className="submit" type="submit">
              Register
            </button>
          </div>
        </form>
      </main>
    </div>
  );
};

export default Register;
