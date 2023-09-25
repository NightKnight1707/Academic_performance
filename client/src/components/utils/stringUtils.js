export const shortName = ({last_name, first_name, patronymic}) => {
    return `${last_name} ${first_name[0]}. ${patronymic[0]}.`
}