import { useState } from "react";
import "../index.css";

const SignUp = () => {
    const [form, setForm] = useState({ username: '', password: '' });

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('Form submitted:', form);
    };

    return (
        <div>
            <div className="text-3xl font-bold">Sign up</div>
                <form onSubmit={handleSubmit}>
                    <div>
                        <label>
                            Username:
                            <input
                                type="text"
                                name="username"
                                value={form.username}
                                onChange={handleChange}
                                required
                                className="border"
                            />
                        </label>
                    </div>
                    <div>
                        <label>
                            Password:
                            <input
                                type="password"
                                name="password"
                                value={form.password}
                                onChange={handleChange}
                                className="border"
                                required/>
                        </label>
                    </div>
                    <button className="border">Sign Up</button>
                </form>
        </div>
    );
};

export default SignUp;