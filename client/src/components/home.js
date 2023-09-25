import {useEffect, useState} from "react";
import axios from "axios";
import {StudentView} from "./marks/studentMarksView";
import ProfessorView from "./marks/professorView";


export const Home = ({user, setUser}) => {


    useEffect(() => {
        if(localStorage.getItem('access_token') === null){
            window.location.href = '/login'
        }
    }, []);

    const uRole = user && user.user.role;

    return (
        <div className="form-signin mt-5">
            {
                uRole === "student" ? <StudentView studentId={user.pk} /> : null
            }
            {
                uRole === "professor" ? <ProfessorView professorId={user.pk} /> : null
            }
        </div>
    )

}