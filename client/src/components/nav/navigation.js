import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import React, {useState, useEffect, createContext, useContext} from 'react';
import {shortName} from "../utils/stringUtils";
import axios from "axios";

const ROLE_MAP = {
    "admin": "Администратор",
    "student": "Студент",
    "professor": "Профессор",
}

export function Navigation({user, setUser}) {
    const [isAuth, setIsAuth] = useState(false);
    const [isProfessor, setIsProfessor] = useState(false);

    useEffect(() => {
        if (localStorage.getItem('access_token') !== null) {
            setIsAuth(true);
            (async () => {
                try {
                    const {data} = await
                        axios.get('/api/v1/auth/users',
                            {
                                headers:
                                    {
                                        'Content-Type': 'application/json',
                                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                                    }
                            })
                    localStorage.setItem('user', JSON.stringify(data));
                    setUser(data)
                    if (data && data.user.role === "professor") {
                        setIsProfessor(true)
                    }
                } catch (e) {
                    console.log('not working', e)
                }
            })()

        }


    }, [isAuth]);
    return (
        <div>
            <Navbar className="p-1" bg="dark" variant="dark">
                <Navbar.Brand href="/">Бально-рейтинговая система</Navbar.Brand>
                <Nav>
                    {isAuth ? <Nav.Link href="/">Домой</Nav.Link> : null}
                </Nav>
                <Nav className="me-auto">
                    {isProfessor ? <Nav.Link href="/studmarks">Оценки студента</Nav.Link> : null}
                </Nav>

                <div className={"text-info ms-auto p-1"}>
                    {user ? shortName(user.user) : null}
                </div>
                <div className={"text-secondary"}>
                    {user ? ROLE_MAP[user.user.role] : null}
                </div>
                <Nav>
                    {isAuth ? <Nav.Link href="/logout">Выход</Nav.Link> :
                        <Nav.Link href="/login">Вход</Nav.Link>}
                </Nav>
            </Navbar>
        </div>
    );
}