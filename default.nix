{ python3Packages }:

python3Packages.buildPythonApplication {
  name = "snupirit";
  src = ./.;
  format = "other";

  propagatedBuildInputs = with python3Packages; [
    pycryptodomex
    pwntools
    requests
  ];
  nativeCheckInputs = with python3Packages; [ flake8 mypy types-requests ];

  checkPhase = ''
    runHook preCheck
    mypy --strict snupirit.py
    mypy --ignore-missing-imports --disable-error-code name-defined --strict extract-keys.py
    flake8 snupirit.py
    flake8 --ignore F403,F405 extract-keys.py
    runHook postCheck
  '';

  installPhase = ''
    runHook preInstall
    install -Dm755 snupirit.py $out/bin/snupirit
    install -Dm755 extract-keys.py $out/bin/extract-keys
    runHook postInstall
  '';

  meta.mainProgram = "snupirit";
}
