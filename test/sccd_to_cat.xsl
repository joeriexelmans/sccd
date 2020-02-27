<?xml version="1.0" encoding="UTF-8"?>
<!-- This XSLT transformation transforms SCCD source files to 'SMCAT', a textual format for state-machine-cat, a renderer of state machines -->
<xsl:stylesheet version="2.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:sccd="msdl.uantwerpen.be/sccd">

  <xsl:output method="text"/>
  <xsl:template match="/">
    <xsl:for-each select="sccd:diagram/sccd:class">
      <xsl:apply-templates/>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="sccd:scxml">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="sccd:state|sccd:parallel|sccd:history">

    <xsl:value-of select="@id"/>

    <xsl:if test="sccd:state|sccd:parallel|sccd:history">
      {
        <xsl:if test="@initial">
          initial_<xsl:value-of select="count(ancestor::*)*100+count(preceding-sibling::*)"/>,
        </xsl:if>
        <xsl:apply-templates select="(sccd:state|sccd:parallel|sccd:history)[1]"/>
      }
    </xsl:if>

    <xsl:choose>
      <xsl:when test="following-sibling::sccd:state | following-sibling::sccd:parallel | following-sibling::sccd:history">
        ,
        <xsl:apply-templates select="(following-sibling::sccd:state | following-sibling::sccd:parallel | following-sibling::sccd:history)[1]"/>
      </xsl:when>
      <xsl:otherwise>
        ;
      </xsl:otherwise>
    </xsl:choose>

    <xsl:if test="@initial">
      initial_<xsl:value-of select="count(ancestor::*)*100+count(preceding-sibling::*)"/>
      -> <xsl:value-of select="@initial"/>;
    </xsl:if>

    <xsl:for-each select="sccd:transition">
      <xsl:value-of select="../@id"/> -> <xsl:value-of select="tokenize(@target,'/')[last()]"/>
      <xsl:if test="@event">
        : <xsl:value-of select="@event"/>
      </xsl:if>
      ;
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>

