export default function DwSection({ title, children }) {
  return (
    <div className="dw-sec">
      <div className="sec-h">{title}</div>
      {children}
    </div>
  );
}
