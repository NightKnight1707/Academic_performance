import {useEffect, useState} from "react";
import axios from "axios";
import {shortName} from "../utils/stringUtils";
import {StudentView} from "./studentMarksView";

export const Scroll = (props) => {
    return(
        <div className={"w-25"} style={{overflowY: 'scroll', height:'500px'}}>
            {props.children}
        </div>
    );
}

function SearchList({ students, searchStr, setSelectedStud}) {
    const filtered = students.filter((item) => {
        return item.user.first_name?.includes(searchStr) ||
            item.user.last_name?.includes(searchStr) ||
            item.user.patronymic?.includes(searchStr) ||
            item.user.username?.includes(searchStr) ||
            item.user.email?.includes(searchStr) ||
            item.record_book_number?.includes(searchStr)
    }).map((i, idx) => {
        return (
            <li className="list-group-item list-group-item-action" key={idx} onClick={(event => {setSelectedStud(i)})}>
                {shortName(i.user)}
            </li>
        )
    })

    // const filtered = filteredPersons.map(person => <div></div>);
    return (
        <ul className="list-group m-4">
            {filtered}
        </ul>
    );
}

const StudMarks = () => {

    const [searchStr, setSearchStr] = useState("")
    const [students, setStudents] = useState([])
    const [selectedStud, setSelectedStud] = useState(null)

    useEffect(() => {
        (async () => {
            try {
                const {data} = await
                    axios.get(`/api/v1/auth/users/students`,
                        {
                            headers:
                                {
                                    'Content-Type': 'application/json',
                                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                                }
                        })
                setStudents(data)
            } catch (e) {
                console.log('not working', e)
            }
        })()
    }, [])

    const handleSearchChange = (e) => {
        setSearchStr(e.target.value)
    }


    return (
        <>
            {selectedStud ? (
                <>
                    <h3 className={"label label-default m-4"}>Студент выбран:</h3>
                    <h5 className={"label label-default ms-4"}>{shortName(selectedStud.user)}</h5>
                    <button className={"btn btn-primary ms-4 mt-1"} onClick={(event => {setSelectedStud(null)})}>Отмена</button>
                    <div className={"mt-3"}/>
                    <StudentView studentId={selectedStud.pk} />
                </>
            ) : (
                <>
                    <input
                        className="form-control w-25 m-4"
                        type="search"
                        placeholder="Найти студента"
                        onChange={handleSearchChange}
                    />

                    <Scroll>
                        <SearchList students={students} searchStr={searchStr} setSelectedStud={setSelectedStud}/>
                    </Scroll>
                </>

            )}
        </>
    )
}

export default StudMarks;