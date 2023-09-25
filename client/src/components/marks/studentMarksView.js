import {useEffect, useState} from "react";
import axios from "axios";
import {shortName} from "../utils/stringUtils";

export const EDU_LEVELS_MAP = {
    'b': "бакалавриат",
    'm': "магистратура",
    'p': "аспирантура",
    's': "специалитет"
}

export const REPORTING_LEVEL = {
    't': "Зачет",
    'd': "Диф. зачет",
    'e': "Экзамен"
}

const countMean = ({att1, att2, att3, mark_group}) => {
    if (mark_group.reporting_level === "t") {
        return "—"
    }
    return att1 && att2 && att3 && Math.round((att1 + att2 + att3) / 3)
}

const MarkComponent = ({children, isTotal=false}) => {
    let style = {backgroundColor: "rgba(0, 0, 0, 0)"};

    switch (true) {
        case (children === null):
            break
        case (children < (isTotal ? 25 * 2 : 25)):
            style = {backgroundColor: "rgba(255, 0, 0, 0.75)"}
            break
        case (children < (isTotal ? 35 * 2 : 35)):
            style = {backgroundColor: "rgba(255, 193, 7, 0.25)"}
            break
        case (children < (isTotal ? 45 * 2 : 45)):
            style = {backgroundColor: "rgba(0, 128, 128, 0.25)"}
            break
        case (children <= (isTotal ? 50 * 2 : 50)):
            style = {backgroundColor: "rgba(0, 128, 0, 0.25)"};
            break
    }

    return (<td style={style}>{children}</td>)
}

const countAll = ({att1, att2, att3, additional, exam, mark_group}) => {
    if (!(att1 && att2 && att3)) {
        return null
    }

    if (mark_group.reporting_level === "t") {
        return Math.round((att1 + att2 + att3) / 3) * 2
    }
    else if (mark_group.reporting_level === "d") {
        return (Math.round((att1 + att2 + att3) / 3) + additional)  * 2
    }
    else if (mark_group.reporting_level === "e") {
        return Math.round((att1 + att2 + att3) / 3) + exam + additional
    }
}

export const StudentView = ({studentId}) => {
    const [marksInfo, setMarksInfo] = useState([])

    useEffect(() => {
        (async () => {
            try {
                const {data} = await
                    axios.get(`/api/v1/marks/${studentId}`,
                        {
                            headers:
                                {
                                    'Content-Type': 'application/json',
                                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                                }
                        })
                setMarksInfo(data)
            } catch (e) {
                console.log('not working', e)
            }
        })()
    }, [])

    const currStudent = marksInfo.length && marksInfo[0].student

    const userInfoTable = currStudent ? (
        <table className="table table-bordered">
            <thead>
            <tr className={"table-secondary"}>
                <th scope="col">Имя пользователя</th>
                <th scope="col">Фамилия</th>
                <th scope="col">Имя</th>
                <th scope="col">Отчество</th>
                <th scope="col">Почта</th>
                <th scope="col">Год зачисления</th>
                <th scope="col">Номер студенческого</th>
                <th scope="col">Курс</th>
                <th scope="col">Группа</th>
                <th scope="col">Ступень высшего образования</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>{currStudent.user.username}</td>
                <td>{currStudent.user.first_name}</td>
                <td>{currStudent.user.last_name}</td>
                <td>{currStudent.user.patronymic}</td>
                <td>{currStudent.user.email}</td>
                <td>{currStudent.year_of_enrollment}</td>
                <td>{currStudent.record_book_number}</td>
                <td>{currStudent.group.course_number}</td>
                <td>{currStudent.group.group_number}</td>
                <td>{EDU_LEVELS_MAP[currStudent.group.higher_education_level]}</td>
            </tr>

            </tbody>
        </table>
    ) : null

    const studMarks = currStudent ? (
        <table className="table table-bordered">
            <thead>
            <tr className={"table-secondary"}>
                <th scope="col">Семестр</th>
                <th scope="col">Предмет</th>
                <th scope="col">Отчётность</th>
                <th scope="col">Преподаватель</th>
                <th scope="col">1</th>
                <th scope="col">2</th>
                <th scope="col">3</th>
                <th scope="col">взеш. балл</th>
                <th scope="col">Экзамен</th>
                <th scope="col">Доп. балл</th>
                <th scope="col">Итог. балл</th>
            </tr>
            </thead>
            <tbody>
            {
                marksInfo.map((markSection, idx) => {
                    return (
                        <tr key={idx}>
                            <td>{markSection.mark_group.semester}</td>
                            <td>{markSection.mark_group.subject.name}</td>
                            <td>{REPORTING_LEVEL[markSection.mark_group.reporting_level]}</td>
                            <td>{shortName(markSection.mark_group.professor.user)}</td>
                            <MarkComponent>{markSection.att1}</MarkComponent>
                            <MarkComponent>{markSection.att2}</MarkComponent>
                            <MarkComponent>{markSection.att3}</MarkComponent>
                            <MarkComponent>{countMean(markSection)}</MarkComponent>
                            <MarkComponent>{["t", "d"].includes(markSection.mark_group.reporting_level) ? "—" : markSection.exam}</MarkComponent>
                            <td>{markSection.mark_group.reporting_level === "t" ? "—" : markSection.additional || 0}</td>
                            <MarkComponent isTotal={true}>{countAll(markSection)}</MarkComponent>
                        </tr>
                    )
                })
            }
            </tbody>
        </table>
    ) : null

    return (
        <div className={"p-1"}>
            {userInfoTable}
            <div className={"pt-5"} />
            {studMarks}
        </div>
    )
}