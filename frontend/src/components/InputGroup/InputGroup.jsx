import React from "react";

const InputGroup = ({ label, name, type = "text", value, onChange, step }) => (
  <div>
    <label className="block text-sm font-medium text-gray-500 mb-1">
      {label}
    </label>
    <input
      type={type}
      name={name}
      step={step}
      value={value}
      onChange={onChange}
      className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:border-[#5b6bbf] focus:ring-2 focus:ring-indigo-50 outline-none transition-all font-medium text-gray-700"
    />
  </div>
);

export default InputGroup;
