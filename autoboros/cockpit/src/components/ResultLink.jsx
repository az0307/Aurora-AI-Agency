export default function ResultLink({ label, url }) {
  return (
    <div className="dw-sec">
      <div className="sec-h">Result</div>
      <a className="resultlink" href={url} target="_blank" rel="noopener noreferrer">
        ↗ {label}
      </a>
    </div>
  );
}
