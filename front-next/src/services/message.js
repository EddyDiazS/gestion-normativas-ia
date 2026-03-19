"use client";
function Message({ type, text }) {
  return (
    <div className={type === "user" ? "message user" : "message bot"}>
      {text}
    </div>
  );
}

export default Message;
