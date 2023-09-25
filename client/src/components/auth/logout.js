import {useEffect, useState} from "react"
import axios from "axios";

export const Logout = () => {
    useEffect(() => {
        (async () => {
            try {
                localStorage.clear();
                axios.defaults.headers.common['Authorization'] = null;
                window.location.href = '/login'
            } catch (e) {
                console.log('logout not working', e)
            }
        })();
    }, []);
    return (
        <div/>
    )
}