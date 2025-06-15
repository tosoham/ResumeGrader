import Rhombus from "../assets/Rhombus.gif"

export function Spinner(){
    
    return(
        <div>
             <div style={{marginTop : "5rem",marginLeft: "14.5rem"}}>
                    <img src={Rhombus} alt="loading" />
             </div>
        </div>
    )
}