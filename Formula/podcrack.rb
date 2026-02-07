class Podcrack < Formula
  desc "Apple Podcast Transcript Extractor"
  homepage "https://github.com/maximbilan/podcrack"
  url "https://github.com/maximbilan/podcrack/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "0019dfc4b32d63c1392aa264aed2253c1e0c2fb09216f8e2cc269bbfb8bb49b5"
  license "MIT"
  head "https://github.com/maximbilan/podcrack.git", branch: "main"

  depends_on "python@3.10"

  def install
    python3 = Formula["python@3.10"].opt_bin/"python3.10"
    system python3, "-m", "pip", "install", *std_pip_args, "."
  end

  test do
    # Verify the command exists and can be executed
    # podcrack is interactive, so we just check it runs
    output = shell_output("#{bin}/podcrack 2>&1", 1)
    assert_match "podcrack", output
  end
end
