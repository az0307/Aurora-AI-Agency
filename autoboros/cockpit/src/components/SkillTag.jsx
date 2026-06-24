export default function SkillTag({ skill }) {
  if (!skill) return null;
  return <span className="skilltag">skill: {skill}</span>;
}
