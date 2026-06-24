export default function Scrim({ show, onClick }) {
  return <div className={`scrim ${show ? 'show' : ''}`} onClick={onClick} />;
}
