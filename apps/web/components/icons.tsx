import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

function Icon({ children, ...props }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      height="20"
      viewBox="0 0 24 24"
      width="20"
      {...props}
    >
      {children}
    </svg>
  );
}

export function MarkIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M7 5.5 12 2l5 3.5v5L12 14l-5-3.5v-5Z" stroke="currentColor" strokeWidth="1.5" />
      <path d="m7 13.5 5 3.5 5-3.5v5L12 22l-5-3.5v-5Z" stroke="currentColor" strokeWidth="1.5" />
      <path d="M12 7.5v4M9.8 9.5h4.4" stroke="currentColor" strokeLinecap="round" />
    </Icon>
  );
}

export function SearchIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <circle cx="10.8" cy="10.8" r="6.3" stroke="currentColor" strokeWidth="1.7" />
      <path d="m15.5 15.5 4 4" stroke="currentColor" strokeLinecap="round" strokeWidth="1.7" />
    </Icon>
  );
}

export function GraphIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <circle cx="6" cy="7" r="2" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="18" cy="5" r="2" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="17" cy="18" r="2" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="7" cy="17" r="2" stroke="currentColor" strokeWidth="1.5" />
      <path d="m8 6.7 8-1.4M7.5 8.8l8 7.3M9 17h6M6.2 9v6" stroke="currentColor" strokeWidth="1.4" />
    </Icon>
  );
}

export function FlaskIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M9 3h6M10 3v6l-5 9.3A1.8 1.8 0 0 0 6.6 21h10.8a1.8 1.8 0 0 0 1.6-2.7L14 9V3" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" />
      <path d="M7.5 15h9" stroke="currentColor" strokeWidth="1.5" />
    </Icon>
  );
}

export function BookIcon(props: IconProps) {
  return (
    <Icon {...props}>
      <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v16H6.5A2.5 2.5 0 0 0 4 21.5v-16ZM20 5.5A2.5 2.5 0 0 0 17.5 3H13v16h4.5a2.5 2.5 0 0 1 2.5 2.5v-16Z" stroke="currentColor" strokeLinejoin="round" strokeWidth="1.5" />
    </Icon>
  );
}
