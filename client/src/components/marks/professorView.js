import {useEffect, useState} from "react";
import axios from "axios";
import {shortName} from "../utils/stringUtils";

const Scroll = (props) => {
    return(
        <div className={"w-50"} style={{overflowY: 'scroll', height:'500px'}}>
            {props.children}
        </div>
    );
}

const MarksForm = ({marks}) => {
    const [m, setM] = useState(marks)
    const [active, setActive] = useState(true)

    const handleChange = (e) => {
        setActive(true)
        setM((prevState) => {
            return {
                ...prevState,
                [e.target.name]: e.target.value
            }
        })
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const {data} = await
            axios.put(`/api/v1/marks/professor/${m.id}`,
                m,
                {
                    headers:
                        {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                        }
                })
            setM(data)
            setActive(false)
            alert("Данные обновлены!")
        } catch (e) {
            console.log('not working', e)
        }
    }

    return (
        <div className={"border w-100 ms-4"}>
            <h6 className={"m-2"}>{shortName(marks.student.user)}</h6>
            <form onSubmit={handleSubmit}>
                <div className="row p-1">
                    <div className="form-group col">
                        <label>Атт. 1</label>
                        <input type="number" name={"att1"} value={m.att1} max={50} min={0} className="form-control" onChange={handleChange}/>
                    </div>
                    <div className="form-group col">
                        <label>Атт. 2</label>
                        <input type="number" name={"att2"} value={m.att2} max={50} min={0} className="form-control" onChange={handleChange}/>
                    </div>
                    <div className="form-group col">
                        <label>Атт. 3</label>
                        <input type="number" name={"att3"} value={m.att3} max={50} min={0} className="form-control" onChange={handleChange}/>
                    </div>
                    {
                        marks.mark_group.reporting_level !== "t" ? (
                            <div className="form-group col">
                                <label>Доп. баллы</label>
                                <input type="number" name={"additional"} value={m.additional} max={50} min={0} className="form-control" onChange={handleChange}/>
                            </div>
                        ) : null
                    }

                    {
                        marks.mark_group.reporting_level === "e" ? (
                            <div className="form-group col">
                                <label>Экзамен</label>
                                <input type="number" name={"exam"} max={50} value={m.exam} min={0} className="form-control" onChange={handleChange}/>
                            </div>
                        ) : null
                    }

                </div>
                <button type="submit" disabled={!active} className="btn btn-primary col m-1">Подтвердить</button>
            </form>
        </div>
    )
}

const MarksList = ({studentMarks}) => {
    return (
        <>
            <h2 className={"label label-default ms-4"}>
                Список студентов:
            </h2>
            {
                studentMarks.map((i, idx) => {
                    return <MarksForm marks={i} key={idx} />
                })
            }
        </>
    )
}


const GMList = ({groupMarks, searchStr, setSelectedGM, getStudentsByGroup}) => {
    const filtered = groupMarks.filter((item) => {
        return item.group?.course_number?.toString()?.includes(searchStr) ||
            item.group?.group_number?.toString()?.includes(searchStr) ||
            item.semester?.toString()?.includes(searchStr) ||
            item.subject?.name?.toString()?.includes(searchStr)
    }).map((i, idx) => {
        return (
            <li className="list-group-item list-group-item-action" key={idx} onClick={(event => {
                setSelectedGM(i)
                getStudentsByGroup(i)
            })}>
                {`${i.subject.name} Группа ${i.group.group_number} Семестр ${i.semester}`}
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

const ProfessorView = ({professorId}) => {
    const [groupMarks, setGroupMarks] = useState([])
    const [selectedGM, setSelectedGM] = useState(null)
    const [searchStr, setSearchStr] = useState("")
    const [studentMarks, setStudentMarks] = useState([])

    useEffect(() => {
        (async () => {
            try {
                const {data} = await
                    axios.get(`/api/v1/marks/professor`,
                        {
                            headers:
                                {
                                    'Content-Type': 'application/json',
                                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                                }
                        })
                setGroupMarks(data)
            } catch (e) {
                console.log('not working', e)
            }
        })()
    }, [selectedGM])

    const handleSearchChange = (e) => {
        setSearchStr(e.target.value)
    }

    const getStudentsByGroup = async (g) => {
        try {
            const {data} = await
                axios.get(`/api/v1/marks/professor/${g.id}`,
                    {
                        headers:
                            {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                            }
                    })
            setStudentMarks(data)
        } catch (e) {
            console.log('not working', e)
        }
    }

    return (
        <>
            {
                selectedGM ? (
                    <div className={"w-75"}>
                        <h3 className={"label label-default m-4"}>Группа выбрана:</h3>
                        <h5 className={"label label-default ms-4"}>{`${selectedGM.subject.name} Группа ${selectedGM.group.group_number} Семестр ${selectedGM.semester}`}</h5>
                        <button className={"btn btn-primary ms-4 mt-1"} onClick={(event => {setSelectedGM(null)})}>Отмена</button>
                        <div className={"mt-3"}/>
                        <MarksList studentMarks={studentMarks} />
                    </div>
                ) : (
                    <>
                        <input
                            className="form-control w-50 m-4"
                            type="search"
                            placeholder="Поиск групп"
                            onChange={handleSearchChange}
                        />

                        <Scroll>
                            <GMList groupMarks={groupMarks} searchStr={searchStr} setSelectedGM={setSelectedGM} getStudentsByGroup={getStudentsByGroup}/>
                        </Scroll>
                    </>
                )
            }
        </>
    )
}

export default ProfessorView;