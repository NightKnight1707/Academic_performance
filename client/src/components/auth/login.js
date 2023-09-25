// Import the react JS packages
import axios from "axios";
import {useState} from "react";
// Define the Login function.
export const Login = ({setUser}) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errors, setErrors] = useState([])
    // Create the submit method.
    const submit = async e => {
        e.preventDefault();
        setErrors([])
        const user = {
            username: username,
            password: password
        };
        // Create the POST requuest
        try {
            const {data} = await
                axios.post('/api/v1/jwt/create/',
                    user,
                    {
                        headers:
                            {'Content-Type': 'application/json'}
                    })

            // Initialize the access & refresh token in localstorage.
            localStorage.clear();
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            axios.defaults.headers.common['Authorization'] =
                `Bearer ${data['access']}`;
            window.location.href = '/'
        }
        catch (e) {
            setErrors(["Ошибка входа, проверьте данные!"])
            console.log(e)
        }

    }
    return (
        <div className="Auth-form-container">
            <form className="Auth-form" onSubmit={submit}>
                <div className="Auth-form-content">
                    <h3 className="Auth-form-title">Вход</h3>
                    <div className="form-group mt-3">
                        <label>Имя пользователя</label>
                        <input className="form-control mt-1"
                               placeholder="Введите имя пользователя"
                               name='username'
                               type='text' value={username}
                               required
                               onChange={e => setUsername(e.target.value)}/>
                    </div>
                    <div className="form-group mt-3">
                        <label>Пароль</label>
                        <input name='password'
                               type="password"
                               className="form-control mt-1"
                               placeholder="Введите пароль"
                               value={password}
                               required
                               onChange={e => setPassword(e.target.value)}/>
                    </div>
                    <div>
                        {errors.map((i, idx) => {
                            return <div className={"text-center text-danger mt-3"} key={idx}>{i}</div>
                        })}
                    </div>
                    <div className="d-grid gap-2 mt-3">
                        <button type="submit"
                                className="btn btn-primary">Войти
                        </button>
                    </div>
                </div>
            </form>
        </div>
    )
}