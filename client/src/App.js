import './App.css';
import {BrowserRouter, Routes, Route} from 'react-router-dom'
import {Navigation} from "./components/nav/navigation";
import {Login} from "./components/auth/login";
import {Logout} from "./components/auth/logout";
import {Home} from "./components/home";
import {useState} from "react";
import StudMarks from "./components/marks/professorToStudentMarksView";

function App() {
    const [user, setUser] = useState(null)
    return (
        <BrowserRouter>
            <Navigation user={user} setUser={setUser}/>
            <Routes>
                <Route path="/" element={<Home user={user} setUser={setUser}/>}/>
                <Route path="/login" element={<Login setUser={setUser}/>}/>
                <Route path="/logout" element={<Logout/>}/>
                <Route path="/studmarks" element={<StudMarks/>}/>
            </Routes>
        </BrowserRouter>
    )

}

export default App;